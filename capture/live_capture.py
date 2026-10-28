"""
capture/live_capture.py
-----------------------
Live network traffic capture module (CN-016).

Captures live packets from network interfaces and saves them as PCAP files
for subsequent flow extraction and classification.

⚠️ REQUIRES: Npcap driver + Administrator privileges (Windows)
"""

import logging
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from scapy.all import sniff, wrpcap, conf as scapy_conf
from scapy.error import Scapy_Exception

from common.errors import CaptureError
from common.logging_setup import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class LiveCapture:
    """
    Live network traffic capture.
    
    Captures packets from a network interface and saves them as PCAP files.
    Uses Scapy for cross-platform packet capture.
    
    Parameters
    ----------
    interface : str, optional
        Network interface name (e.g., "Ethernet", "Wi-Fi").
        If None, uses default interface.
    packet_count : int, optional
        Number of packets to capture (0 = unlimited until stopped)
    timeout : int, optional
        Capture timeout in seconds (None = no timeout)
    bpf_filter : str, optional
        Berkeley Packet Filter expression for selective capture
        (e.g., "tcp port 80" for HTTP only)
    
    Examples
    --------
    >>> capture = LiveCapture(packet_count=1000)
    >>> pcap_path = capture.capture(output_path=Path("capture.pcap"))
    >>> print(f"Captured to: {pcap_path}")
    """
    
    def __init__(
        self,
        interface: Optional[str] = None,
        packet_count: int = 1000,
        timeout: Optional[int] = 60,
        bpf_filter: Optional[str] = None
    ):
        self.interface = interface or self._get_default_interface()
        self.packet_count = packet_count
        self.timeout = timeout
        self.bpf_filter = bpf_filter
        
        logger.info(f"LiveCapture initialized: interface={self.interface}, count={packet_count}")
    
    def _get_default_interface(self) -> str:
        """
        Get default network interface.
        
        Returns
        -------
        str
            Default interface name
            
        Raises
        ------
        CaptureError
            If no interface available
        """
        try:
            iface = scapy_conf.iface
            if iface:
                logger.debug(f"Default interface: {iface}")
                return iface
            else:
                raise CaptureError("No default interface found")
        except Exception as e:
            raise CaptureError(f"Failed to get default interface: {e}")
    
    def list_interfaces(self) -> List[str]:
        """
        List available network interfaces.
        
        Returns
        -------
        List[str]
            List of interface names
        """
        try:
            from scapy.arch import get_if_list
            interfaces = get_if_list()
            logger.info(f"Available interfaces: {interfaces}")
            return interfaces
        except Exception as e:
            logger.error(f"Failed to list interfaces: {e}")
            return []
    
    def capture(
        self,
        output_path: Path,
        verbose: bool = False
    ) -> Path:
        """
        Capture live traffic and save to PCAP file.
        
        Parameters
        ----------
        output_path : Path
            Path to save PCAP file
        verbose : bool
            Print packet summary during capture
            
        Returns
        -------
        Path
            Path to saved PCAP file
            
        Raises
        ------
        CaptureError
            If capture fails
        """
        logger.info(f"Starting capture on {self.interface}...")
        logger.info(f"  Count: {self.packet_count} packets")
        logger.info(f"  Timeout: {self.timeout}s")
        logger.info(f"  Filter: {self.bpf_filter or 'none'}")
        logger.info(f"  Output: {output_path}")
        
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Capture packets
            packets = sniff(
                iface=self.interface,
                count=self.packet_count,
                timeout=self.timeout,
                filter=self.bpf_filter,
                prn=lambda x: x.summary() if verbose else None
            )
            
            # Save to PCAP
            wrpcap(str(output_path), packets)
            
            logger.info(f"✅ Captured {len(packets)} packets")
            logger.info(f"✅ Saved to: {output_path}")
            logger.info(f"   File size: {output_path.stat().st_size:,} bytes")
            
            return output_path
            
        except Scapy_Exception as e:
            if "tcpdump is not available" in str(e):
                raise CaptureError(
                    "Live capture requires Npcap driver.\n"
                    "Download from: https://npcap.com/\n"
                    "Install with 'WinPcap API-compatible mode' enabled."
                )
            else:
                raise CaptureError(f"Scapy capture failed: {e}")
        
        except PermissionError:
            raise CaptureError(
                "Permission denied. Live capture requires Administrator privileges.\n"
                "Run PowerShell/CMD as Administrator."
            )
        
        except Exception as e:
            raise CaptureError(f"Capture failed: {e}")
    
    def capture_duration(
        self,
        output_path: Path,
        duration_seconds: int,
        verbose: bool = False
    ) -> Path:
        """
        Capture traffic for a specific duration.
        
        Parameters
        ----------
        output_path : Path
            Path to save PCAP file
        duration_seconds : int
            Capture duration in seconds
        verbose : bool
            Print packet summary
            
        Returns
        -------
        Path
            Path to saved PCAP file
        """
        # Temporarily override timeout
        original_timeout = self.timeout
        original_count = self.packet_count
        
        self.timeout = duration_seconds
        self.packet_count = 0  # Unlimited
        
        try:
            return self.capture(output_path, verbose=verbose)
        finally:
            # Restore original settings
            self.timeout = original_timeout
            self.packet_count = original_count


def capture_live_traffic(
    output_path: Path,
    packet_count: int = 1000,
    timeout: int = 60,
    interface: Optional[str] = None,
    bpf_filter: Optional[str] = None
) -> Path:
    """
    Convenience function for live capture.
    
    Parameters
    ----------
    output_path : Path
        Path to save PCAP
    packet_count : int
        Number of packets to capture
    timeout : int
        Timeout in seconds
    interface : str, optional
        Network interface
    bpf_filter : str, optional
        BPF filter expression
        
    Returns
    -------
    Path
        Path to saved PCAP file
    """
    capture = LiveCapture(
        interface=interface,
        packet_count=packet_count,
        timeout=timeout,
        bpf_filter=bpf_filter
    )
    return capture.capture(output_path)


def main():
    """CLI interface for live capture."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FlowSentry Live Traffic Capture"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output PCAP file path"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=1000,
        help="Number of packets to capture (default: 1000)"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=60,
        help="Capture timeout in seconds (default: 60)"
    )
    parser.add_argument(
        "--interface", "-i",
        type=str,
        help="Network interface (default: auto-detect)"
    )
    parser.add_argument(
        "--filter", "-f",
        type=str,
        help="BPF filter (e.g., 'tcp port 80')"
    )
    parser.add_argument(
        "--list-interfaces",
        action="store_true",
        help="List available interfaces and exit"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print packet summaries during capture"
    )
    
    args = parser.parse_args()
    
    # List interfaces if requested
    if args.list_interfaces:
        capture = LiveCapture()
        interfaces = capture.list_interfaces()
        print("Available interfaces:")
        for iface in interfaces:
            print(f"  - {iface}")
        sys.exit(0)
    
    # Capture traffic
    print("=" * 70)
    print("FLOWSENTRY LIVE CAPTURE")
    print("=" * 70)
    print(f"Interface: {args.interface or 'auto-detect'}")
    print(f"Packet count: {args.count}")
    print(f"Timeout: {args.timeout}s")
    print(f"Filter: {args.filter or 'none'}")
    print(f"Output: {args.output}")
    print("=" * 70)
    
    try:
        pcap_path = capture_live_traffic(
            output_path=args.output,
            packet_count=args.count,
            timeout=args.timeout,
            interface=args.interface,
            bpf_filter=args.filter
        )
        
        print("\n" + "=" * 70)
        print("✅ CAPTURE COMPLETE")
        print("=" * 70)
        print(f"Saved to: {pcap_path}")
        print(f"Size: {pcap_path.stat().st_size:,} bytes")
        print("\nNext step: Classify the captured traffic")
        print(f"  python -m inference.pcap_classifier --pcap {pcap_path} --output <output_dir>")
        
    except CaptureError as e:
        print(f"\n❌ CAPTURE FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Capture interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
