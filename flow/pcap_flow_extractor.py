"""
flow/pcap_flow_extractor.py
---------------------------
PCAP flow extraction pipeline (CN-014).

Orchestrates:
1. Feature extraction via CICFlowMeter adapter
2. Feature normalization via normalizer
3. Schema validation

Per TRD §9: Ensures train/inference parity through canonical schema.
"""

from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd

from flow.cicflowmeter_adapter import CICFlowMeterAdapter
from flow.normalizer import FlowNormalizer
from common.errors import FlowExtractionError, SchemaMismatchError
from common.logging_setup import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class PcapFlowExtractor:
    """
    Complete PCAP → canonical flow features pipeline.
    
    Combines:
    - CICFlowMeter adapter (raw feature extraction)
    - Normalizer (canonical schema conversion)
    - Validation (schema compliance check)
    
    Parameters
    ----------
    schema_path : Path
        Path to feature_schema.yaml
    extractor_timeout : int
        Timeout for CICFlowMeter (seconds)
        
    Attributes
    ----------
    adapter : CICFlowMeterAdapter
        Feature extractor adapter
    normalizer : FlowNormalizer
        Feature normalizer
    """
    
    def __init__(
        self,
        schema_path: Path = Path("config/feature_schema.yaml"),
        extractor_timeout: int = 300
    ):
        """Initialize PCAP flow extractor."""
        logger.info("Initializing PcapFlowExtractor...")
        
        # Initialize components
        self.adapter = CICFlowMeterAdapter(timeout=extractor_timeout)
        self.normalizer = FlowNormalizer(schema_path=schema_path)
        
        logger.info("PcapFlowExtractor ready")
    
    def extract_flows(
        self,
        pcap_path: Path,
        output_dir: Path | None = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Extract canonical flow features from PCAP file.
        
        Pipeline:
        1. Extract raw features via CICFlowMeter
        2. Normalize to canonical schema
        3. Validate schema compliance
        4. Return features + metadata + stats
        
        Parameters
        ----------
        pcap_path : Path
            Input PCAP file path
        output_dir : Path, optional
            Directory to save intermediate/output files
            
        Returns
        -------
        features : pd.DataFrame
            Canonical feature DataFrame (model input)
        metadata : pd.DataFrame
            Flow metadata (five-tuple, timestamps)
        stats : dict
            Extraction statistics and info
            
        Raises
        ------
        FileNotFoundError
            If PCAP file doesn't exist
        FlowExtractionError
            If extraction fails
        SchemaMismatchError
            If schema validation fails
        """
        logger.info(f"Extracting flows from: {pcap_path}")
        
        # Validate input
        if not pcap_path.exists():
            raise FileNotFoundError(f"PCAP file not found: {pcap_path}")
        
        # Step 1: Extract raw features
        logger.info("Step 1: Extracting raw features via CICFlowMeter...")
        raw_features = self.adapter.extract_flows(pcap_path)
        
        if raw_features.empty:
            logger.warning("CICFlowMeter returned empty DataFrame (no flows)")
            return pd.DataFrame(), pd.DataFrame(), {
                "flow_count": 0,
                "raw_features": 0,
                "canonical_features": 0,
                "status": "empty"
            }
        
        logger.info(f"Extracted {len(raw_features)} flows, {len(raw_features.columns)} raw features")
        
        # Step 2: Normalize to canonical schema
        logger.info("Step 2: Normalizing to canonical schema...")
        features, metadata = self.normalizer.normalize(
            raw_features,
            extractor_name="CICFlowMeter"
        )
        
        logger.info(f"Normalized to {len(features.columns)} canonical features")
        
        # Step 3: Save outputs if requested
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save canonical features
            features_path = output_dir / "features.csv"
            features.to_csv(features_path, index=False)
            logger.info(f"Saved features: {features_path}")
            
            # Save metadata
            if not metadata.empty:
                metadata_path = output_dir / "metadata.csv"
                metadata.to_csv(metadata_path, index=False)
                logger.info(f"Saved metadata: {metadata_path}")
            
            # Save raw features (optional, for debugging)
            raw_path = output_dir / "raw_features.csv"
            raw_features.to_csv(raw_path, index=False)
            logger.debug(f"Saved raw features: {raw_path}")
        
        # Step 4: Compile statistics
        stats = {
            "flow_count": len(features),
            "raw_features": len(raw_features.columns),
            "canonical_features": len(features.columns),
            "metadata_columns": len(metadata.columns),
            "pcap_path": str(pcap_path),
            "extractor": self.adapter.get_extractor_info(),
            "normalizer": self.normalizer.get_feature_info(),
            "status": "success"
        }
        
        logger.info(f"Extraction complete: {stats['flow_count']} flows, {stats['canonical_features']} features")
        
        return features, metadata, stats
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about extraction pipeline.
        
        Returns
        -------
        dict
            Pipeline component information
        """
        return {
            "adapter": self.adapter.get_extractor_info(),
            "normalizer": self.normalizer.get_feature_info()
        }


def extract_flows_from_pcap(
    pcap_path: Path,
    output_dir: Path | None = None,
    schema_path: Path = Path("config/feature_schema.yaml")
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function for PCAP flow extraction.
    
    Parameters
    ----------
    pcap_path : Path
        Input PCAP file
    output_dir : Path, optional
        Output directory for CSVs
    schema_path : Path
        Feature schema path
        
    Returns
    -------
    features : pd.DataFrame
        Canonical features
    metadata : pd.DataFrame
        Flow metadata
    stats : dict
        Extraction statistics
    """
    extractor = PcapFlowExtractor(schema_path=schema_path)
    return extractor.extract_flows(pcap_path, output_dir)
