"""
inference/realtime_classifier.py
---------------------------------
Real-time network traffic classification (CN-017).

Captures live traffic, extracts flow features, and classifies them in real-time
with continuous monitoring and display.
"""

import logging
import sys
import time
from pathlib import Path
from typing import Optional
from datetime import datetime
import signal

import pandas as pd

from capture.live_capture import LiveCapture
from flow.pcap_flow_extractor import extract_flows_from_pcap
from models.registry import load_active_model
from common.errors import CaptureError, ExtractionError, ModelNotFoundError
from common.logging_setup import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class RealtimeClassifier:
    """
    Real-time traffic classification.
    
    Continuously captures traffic, extracts features, and classifies flows
    in real-time with live display of results.
    
    Parameters
    ----------
    interface : str, optional
        Network interface to capture from
    capture_window : int
        Capture window duration in seconds (default: 10)
    packet_count : int
        Packets per capture window (default: 1000)
    bpf_filter : str, optional
        BPF filter for selective capture
    output_dir : Path, optional
        Directory to save capture files and results
    
    Examples
    --------
    >>> classifier = RealtimeClassifier(capture_window=10)
    >>> classifier.start()  # Runs until interrupted
    """
    
    def __init__(
        self,
        interface: Optional[str] = None,
        capture_window: int = 10,
        packet_count: int = 1000,
        bpf_filter: Optional[str] = None,
        output_dir: Optional[Path] = None
    ):
        self.interface = interface
        self.capture_window = capture_window
        self.packet_count = packet_count
        self.bpf_filter = bpf_filter
        self.output_dir = output_dir or Path("artifacts/realtime")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load ML model
        self.model = None
        self.model_metadata = None
        
        # Statistics
        self.total_windows = 0
        self.total_flows = 0
        self.class_counts = {}
        
        # Control
        self.running = False
        
        logger.info(f"RealtimeClassifier initialized")
        logger.info(f"  Interface: {interface or 'auto-detect'}")
        logger.info(f"  Capture window: {capture_window}s")
        logger.info(f"  Packet count: {packet_count}")
    
    def load_model(self):
        """Load the active ML model from registry."""
        try:
            logger.info("Loading model from registry...")
            self.model = load_active_model()
            # Get model metadata
            from models.registry import get_active_model_metadata
            self.model_metadata = get_active_model_metadata()
            logger.info(f"✅ Loaded model: {self.model_metadata.get('model_name', 'unknown')}")
        except ModelNotFoundError as e:
            raise RuntimeError(f"No model found: {e}")
    
    def capture_window_traffic(self, window_num: int) -> Optional[Path]:
        """
        Capture one window of traffic.
        
        Parameters
        ----------
        window_num : int
            Window number for filename
            
        Returns
        -------
        Path or None
            Path to captured PCAP, or None if capture failed
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pcap_path = self.output_dir / f"window_{window_num:04d}_{timestamp}.pcap"
        
        try:
            capture = LiveCapture(
                interface=self.interface,
                packet_count=self.packet_count,
                timeout=self.capture_window,
                bpf_filter=self.bpf_filter
            )
            
            logger.info(f"\n{'='*70}")
            logger.info(f"CAPTURE WINDOW {window_num} - {timestamp}")
            logger.info(f"{'='*70}")
            
            return capture.capture(pcap_path, verbose=False)
            
        except CaptureError as e:
            logger.error(f"Capture failed: {e}")
            return None
    
    def classify_window(self, pcap_path: Path) -> Optional[pd.DataFrame]:
        """
        Extract and classify flows from captured traffic.
        
        Parameters
        ----------
        pcap_path : Path
            Path to PCAP file
            
        Returns
        -------
        DataFrame or None
            Predictions DataFrame, or None if failed
        """
        try:
            # Extract flows
            logger.info("Extracting flows...")
            features, metadata, stats = extract_flows_from_pcap(
                pcap_path=pcap_path,
                output_dir=self.output_dir
            )
            
            flow_count = stats.get("flow_count", 0)
            
            if flow_count == 0:
                logger.warning("No flows extracted")
                return None
            
            logger.info(f"✅ Extracted {flow_count} flows")
            
            # Classify
            logger.info("Classifying flows...")
            predictions = self.model.predict(features)
            confidences = self.model.predict_proba(features).max(axis=1)
            
            # Build results
            results = pd.DataFrame({
                'flow_id': range(len(predictions)),
                'predicted_class': predictions,
                'confidence': confidences
            })
            
            # Add metadata
            for col in ['src_ip', 'src_port', 'dst_ip', 'dst_port', 'protocol']:
                if col in metadata.columns:
                    results[col] = metadata[col].values
            
            return results
            
        except ExtractionError as e:
            logger.error(f"Flow extraction failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return None
    
    def display_results(self, results: pd.DataFrame, window_num: int):
        """
        Display classification results.
        
        Parameters
        ----------
        results : DataFrame
            Classification results
        window_num : int
            Window number
        """
        # Count flows per class
        class_counts = results['predicted_class'].value_counts().to_dict()
        
        # Update totals
        self.total_flows += len(results)
        for cls, count in class_counts.items():
            self.class_counts[cls] = self.class_counts.get(cls, 0) + count
        
        # Display
        print(f"\n{'='*70}")
        print(f"WINDOW {window_num} RESULTS")
        print(f"{'='*70}")
        print(f"Total flows: {len(results)}")
        print(f"\nFlows per class:")
        
        for cls in sorted(class_counts.keys()):
            count = class_counts[cls]
            pct = count / len(results) * 100
            bar = '█' * int(pct / 2)
            print(f"  {cls:20s}: {count:4d} ({pct:5.1f}%)  {bar}")
        
        avg_conf = results['confidence'].mean()
        print(f"\nAverage confidence: {avg_conf:.4f}")
        
        # Show a few examples
        print(f"\nSample flows:")
        sample = results.head(3)
        for idx, row in sample.iterrows():
            print(f"  {row['src_ip']:15s}:{row['src_port']:5d} → "
                  f"{row['dst_ip']:15s}:{row['dst_port']:5d}  "
                  f"{row['predicted_class']:15s} ({row['confidence']:.3f})")
    
    def display_summary(self):
        """Display overall statistics."""
        print(f"\n{'='*70}")
        print(f"SESSION SUMMARY")
        print(f"{'='*70}")
        print(f"Total windows: {self.total_windows}")
        print(f"Total flows classified: {self.total_flows}")
        print(f"\nOverall class distribution:")
        
        for cls in sorted(self.class_counts.keys()):
            count = self.class_counts[cls]
            pct = count / self.total_flows * 100 if self.total_flows > 0 else 0
            bar = '█' * int(pct / 2)
            print(f"  {cls:20s}: {count:4d} ({pct:5.1f}%)  {bar}")
    
    def start(self):
        """
        Start real-time classification.
        
        Runs continuously until interrupted (Ctrl+C).
        """
        print("=" * 70)
        print("FLOWSENTRY REAL-TIME CLASSIFICATION")
        print("=" * 70)
        print(f"Interface: {self.interface or 'auto-detect'}")
        print(f"Capture window: {self.capture_window}s")
        print(f"Packet count: {self.packet_count} per window")
        print(f"Filter: {self.bpf_filter or 'none'}")
        print(f"Output: {self.output_dir}")
        print("=" * 70)
        print("\nPress Ctrl+C to stop\n")
        
        # Load model
        try:
            self.load_model()
        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)
        
        # Set up signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\n\n⚠️ Stopping capture...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start monitoring
        self.running = True
        window_num = 1
        
        while self.running:
            try:
                # Capture window
                pcap_path = self.capture_window_traffic(window_num)
                
                if pcap_path:
                    # Classify
                    results = self.classify_window(pcap_path)
                    
                    if results is not None and len(results) > 0:
                        # Display results
                        self.display_results(results, window_num)
                        self.total_windows += 1
                    
                    # Clean up PCAP (optional - save disk space)
                    # pcap_path.unlink()
                
                window_num += 1
                
                # Brief pause between windows
                time.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Window {window_num} failed: {e}")
                continue
        
        # Display summary
        self.display_summary()
        
        print(f"\n✅ Monitoring stopped")
        print(f"Captured files saved to: {self.output_dir}")


def main():
    """CLI interface for real-time classification."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FlowSentry Real-Time Traffic Classification"
    )
    parser.add_argument(
        "--interface", "-i",
        type=str,
        help="Network interface (default: auto-detect)"
    )
    parser.add_argument(
        "--window", "-w",
        type=int,
        default=10,
        help="Capture window duration in seconds (default: 10)"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=1000,
        help="Packets per window (default: 1000)"
    )
    parser.add_argument(
        "--filter", "-f",
        type=str,
        help="BPF filter (e.g., 'tcp port 80')"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("artifacts/realtime"),
        help="Output directory (default: artifacts/realtime)"
    )
    
    args = parser.parse_args()
    
    # Create classifier
    classifier = RealtimeClassifier(
        interface=args.interface,
        capture_window=args.window,
        packet_count=args.count,
        bpf_filter=args.filter,
        output_dir=args.output
    )
    
    # Start monitoring
    try:
        classifier.start()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
