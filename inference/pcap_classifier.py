"""
inference/pcap_classifier.py
---------------------------
PCAP classification module (CN-015).

Classifies flows from PCAP files using trained models from registry.

Pipeline:
1. Load model from registry (with integrity check)
2. Extract flows from PCAP via flow extractor
3. Apply preprocessing pipeline (loaded with model)
4. Generate predictions
5. Output per-flow classifications + summary

Per TRD §21: PCAP Inference CLI and pipeline.
"""

import argparse
from pathlib import Path
from typing import Dict, Any, Tuple
from datetime import datetime
import pandas as pd
import json

from flow.pcap_flow_extractor import PcapFlowExtractor
from models.registry import load_model
from common.errors import FlowExtractionError, SchemaMismatchError, RegistryIntegrityError
from common.logging_setup import setup_logging
from common.paths import ProjectPaths
from common.config import load_config
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class PcapClassifier:
    """
    PCAP file classifier using trained ML models.
    
    Loads a model from registry and classifies flows from PCAP files.
    
    Parameters
    ----------
    model_id : str | None
        Model ID from registry (if None, uses active model)
    registry_dir : Path | None
        Registry directory (if None, uses default)
        
    Attributes
    ----------
    model : object
        Loaded scikit-learn pipeline
    model_metadata : dict
        Model metadata from registry
    extractor : PcapFlowExtractor
        PCAP flow extractor
    """
    
    def __init__(self, model_id: str | None = None, registry_dir: Path | None = None):
        """Initialize PCAP classifier."""
        logger.info("Initializing PcapClassifier...")
        
        # Note: registry_dir parameter is ignored, kept for API compatibility
        # load_model() uses ProjectPaths internally
        
        logger.info(f"Loading model from registry: {model_id or 'active'}")
        # load_model returns: (pipeline, metadata, feature_schema, label_encoder)
        self.model, self.model_metadata, self.feature_schema, self.label_encoder = load_model(
            model_id=model_id
        )
        
        logger.info(f"Loaded model: {self.model_metadata['model_name']} ({self.model_metadata['model_id']})")
        
        # Initialize flow extractor
        self.extractor = PcapFlowExtractor()
        
        logger.info("PcapClassifier ready")
    
    def classify_pcap(
        self,
        pcap_path: Path,
        output_dir: Path | None = None,
        include_confidence: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Classify flows from a PCAP file.
        
        Parameters
        ----------
        pcap_path : Path
            Input PCAP file
        output_dir : Path, optional
            Directory to save outputs (predictions CSV, summary JSON)
        include_confidence : bool
            Include prediction probabilities (if model supports)
            
        Returns
        -------
        predictions : pd.DataFrame
            Per-flow predictions with metadata
        summary : dict
            Classification summary statistics
            
        Raises
        ------
        FileNotFoundError
            If PCAP doesn't exist
        FlowExtractionError
            If flow extraction fails
        SchemaMismatchError
            If features don't match model schema
        """
        logger.info(f"Classifying PCAP: {pcap_path}")
        
        # Step 1: Extract flows
        logger.info("Step 1: Extracting flows from PCAP...")
        features, metadata, extraction_stats = self.extractor.extract_flows(pcap_path)
        
        if features.empty:
            logger.warning("No flows extracted from PCAP")
            return pd.DataFrame(), {
                "pcap_path": str(pcap_path),
                "flow_count": 0,
                "status": "empty",
                "model_id": self.model_metadata['model_id']
            }
        
        logger.info(f"Extracted {len(features)} flows")
        
        # Step 2: Schema parity check
        logger.info("Step 2: Validating feature schema...")
        self._validate_schema(features)
        
        # Step 3: Generate predictions
        logger.info("Step 3: Generating predictions...")
        predictions_df = self._predict(features, metadata, include_confidence)
        
        # Step 4: Create summary
        summary = self._create_summary(
            predictions_df,
            pcap_path,
            extraction_stats
        )
        
        # Step 5: Save outputs if requested
        if output_dir:
            self._save_outputs(predictions_df, summary, output_dir)
        
        logger.info(f"Classification complete: {len(predictions_df)} flows classified")
        
        return predictions_df, summary
    
    def _validate_schema(self, features: pd.DataFrame):
        """
        Validate feature schema matches model.
        
        Parameters
        ----------
        features : pd.DataFrame
            Extracted features
            
        Raises
        ------
        SchemaMismatchError
            If features don't match model's expected schema
        """
        # Get expected features from model metadata
        expected_features = self.model_metadata.get('selected_features', [])
        
        if not expected_features:
            logger.warning("Model metadata missing 'selected_features', skipping schema check")
            return
        
        # Check for missing features
        actual_features = set(features.columns)
        expected_features_set = set(expected_features)
        
        missing = expected_features_set - actual_features
        extra = actual_features - expected_features_set
        
        if missing:
            error_msg = (
                f"Schema validation failed: {len(missing)} required features missing.\n"
                f"Missing features: {sorted(missing)}\n"
                f"Expected: {len(expected_features)} features\n"
                f"Got: {len(actual_features)} features"
            )
            logger.error(error_msg)
            raise SchemaMismatchError(error_msg)
        
        if extra:
            logger.warning(f"Extra features present (will be ignored): {sorted(extra)}")
        
        logger.info(f"Schema validation passed: {len(expected_features)} features matched")
    
    def _predict(
        self,
        features: pd.DataFrame,
        metadata: pd.DataFrame,
        include_confidence: bool
    ) -> pd.DataFrame:
        """
        Generate predictions for flows.
        
        Parameters
        ----------
        features : pd.DataFrame
            Flow features
        metadata : pd.DataFrame
            Flow metadata
        include_confidence : bool
            Include prediction probabilities
            
        Returns
        -------
        pd.DataFrame
            Predictions with metadata
        """
        # Make predictions
        predictions = self.model.predict(features)
        
        # Build output DataFrame
        result = pd.DataFrame({
            'predicted_class': predictions
        })
        
        # Add confidence scores if requested
        if include_confidence and hasattr(self.model, 'predict_proba'):
            try:
                probabilities = self.model.predict_proba(features)
                # Get max probability (confidence)
                confidences = probabilities.max(axis=1)
                result['confidence'] = confidences
                
                # Add per-class probabilities (optional, can be large)
                classes = self.model.classes_
                for i, cls in enumerate(classes):
                    result[f'prob_{cls}'] = probabilities[:, i]
                
            except Exception as e:
                logger.warning(f"Failed to get prediction probabilities: {e}")
        
        # Add metadata if available
        if not metadata.empty:
            # Combine with metadata
            result = pd.concat([metadata.reset_index(drop=True), result], axis=1)
        
        return result
    
    def _create_summary(
        self,
        predictions: pd.DataFrame,
        pcap_path: Path,
        extraction_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create classification summary.
        
        Parameters
        ----------
        predictions : pd.DataFrame
            Predictions DataFrame
        pcap_path : Path
            Input PCAP path
        extraction_stats : dict
            Extraction statistics
            
        Returns
        -------
        dict
            Summary statistics
        """
        # Count flows per class
        class_counts = predictions['predicted_class'].value_counts().to_dict()
        
        # Calculate average confidence if available
        avg_confidence = None
        if 'confidence' in predictions.columns:
            avg_confidence = predictions['confidence'].mean()
        
        summary = {
            "pcap_path": str(pcap_path),
            "classification_time": datetime.now().isoformat(),
            "model_id": self.model_metadata['model_id'],
            "model_name": self.model_metadata['model_name'],
            "flow_count": len(predictions),
            "flows_per_class": class_counts,
            "average_confidence": avg_confidence,
            "extraction_stats": extraction_stats,
            "status": "success"
        }
        
        return summary
    
    def _save_outputs(
        self,
        predictions: pd.DataFrame,
        summary: Dict[str, Any],
        output_dir: Path
    ):
        """
        Save predictions and summary to files.
        
        Parameters
        ----------
        predictions : pd.DataFrame
            Predictions DataFrame
        summary : dict
            Summary statistics
        output_dir : Path
            Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save predictions CSV
        predictions_path = output_dir / "predictions.csv"
        predictions.to_csv(predictions_path, index=False)
        logger.info(f"Saved predictions: {predictions_path}")
        
        # Save summary JSON
        summary_path = output_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary: {summary_path}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded model.
        
        Returns
        -------
        dict
            Model metadata
        """
        return self.model_metadata


def main():
    """CLI entry point for PCAP classification."""
    parser = argparse.ArgumentParser(
        description="Classify network traffic from PCAP files using trained ML models"
    )
    
    parser.add_argument(
        '--pcap', '-p',
        type=Path,
        required=True,
        help='Input PCAP file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output directory for predictions and summary (default: artifacts/predictions/<pcap_name>)'
    )
    
    parser.add_argument(
        '--model-id', '-m',
        type=str,
        help='Model ID from registry (default: active model)'
    )
    
    parser.add_argument(
        '--no-confidence',
        action='store_true',
        help='Exclude confidence scores from output'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.pcap.exists():
        print(f"[ERROR] PCAP file not found: {args.pcap}")
        return 1
    
    # Default output directory
    if args.output is None:
        config = load_config()
        paths = ProjectPaths(config)
        pcap_name = args.pcap.stem
        args.output = paths.artifacts / 'predictions' / pcap_name
    
    print("=" * 70)
    print("FLOWSENTRY PCAP CLASSIFICATION")
    print("=" * 70)
    print(f"Input PCAP: {args.pcap}")
    print(f"Output directory: {args.output}")
    print(f"Model: {args.model_id or 'active model from registry'}")
    print()
    
    try:
        # Initialize classifier
        print("Loading model from registry...")
        classifier = PcapClassifier(model_id=args.model_id)
        
        model_info = classifier.get_model_info()
        print(f"[OK] Loaded: {model_info['model_name']} ({model_info['model_id']})")
        print()
        
        # Classify PCAP
        print("Classifying flows...")
        predictions, summary = classifier.classify_pcap(
            args.pcap,
            output_dir=args.output,
            include_confidence=not args.no_confidence
        )
        
        # Display summary
        print()
        print("=" * 70)
        print("CLASSIFICATION RESULTS")
        print("=" * 70)
        print(f"Total flows: {summary['flow_count']}")
        print()
        print("Flows per class:")
        for cls, count in summary['flows_per_class'].items():
            percentage = (count / summary['flow_count']) * 100
            bar = '█' * int(percentage / 2)
            print(f"  {cls:20s}: {count:6d} ({percentage:5.1f}%)  {bar}")
        
        if summary['average_confidence']:
            print(f"\nAverage confidence: {summary['average_confidence']:.4f}")
        
        print()
        print(f"[OK] Predictions saved to: {args.output}")
        print("=" * 70)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1
    except FlowExtractionError as e:
        print(f"[ERROR] Flow extraction failed: {e}")
        return 1
    except SchemaMismatchError as e:
        print(f"[ERROR] Schema mismatch: {e}")
        print("\nHint: Model may have been trained with different features.")
        return 1
    except RegistryIntegrityError as e:
        print(f"[ERROR] Registry integrity error: {e}")
        return 1
    except Exception as e:
        logger.exception("Unexpected error during classification")
        print(f"[ERROR] Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
