"""
flow/extractor_base.py
----------------------
Base protocol for flow feature extractors.

Defines the interface that all flow extractors must implement,
following the adapter pattern (TRD §22).
"""

from typing import Protocol, Dict, Any
from pathlib import Path
import pandas as pd


class FlowExtractor(Protocol):
    """
    Protocol for flow feature extraction from PCAPs.
    
    All flow extractors (CICFlowMeter, native Scapy, etc.) must implement
    this interface to ensure consistent behavior across the pipeline.
    
    Methods
    -------
    extract_flows(pcap_path: Path, output_path: Path | None) -> pd.DataFrame
        Extract flow-level features from a PCAP file.
    
    get_extractor_info() -> Dict[str, Any]
        Get metadata about the extractor (version, features, etc.).
    """
    
    def extract_flows(
        self,
        pcap_path: Path,
        output_path: Path | None = None
    ) -> pd.DataFrame:
        """
        Extract flow-level features from a PCAP file.
        
        Parameters
        ----------
        pcap_path : Path
            Path to input PCAP file (.pcap or .pcapng)
        output_path : Path, optional
            Path to save CSV output (if None, return DataFrame only)
            
        Returns
        -------
        pd.DataFrame
            DataFrame with flow features (one row per flow)
            
        Raises
        ------
        FileNotFoundError
            If pcap_path does not exist
        FlowExtractionError
            If extraction fails
        """
        ...
    
    def get_extractor_info(self) -> Dict[str, Any]:
        """
        Get metadata about this extractor.
        
        Returns
        -------
        dict
            Dictionary with keys:
            - name: str (extractor name, e.g., "CICFlowMeter")
            - version: str (extractor version)
            - feature_count: int (number of features extracted)
            - implementation: str (tool/library used)
        """
        ...
