"""
flow/normalizer.py
-----------------
Flow feature normalizer (CN-014).

Converts extractor-specific output (CICFlowMeter CSV) into the canonical
feature schema defined in config/feature_schema.yaml. Handles:
- Column name aliasing (extractor names → canonical names)
- Unit conversions (verified from extractor documentation)
- Derived features (calculated from base features)
- Required feature validation (schema compliance)
- Metadata separation (five-tuple, timestamps kept separate)

Per TRD §9.3: Normalizer ensures train/inference schema parity.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import yaml

from common.errors import SchemaMismatchError, ConfigError
from common.logging_setup import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class FlowNormalizer:
    """
    Normalizer for flow features from extractor output to canonical schema.
    
    Parameters
    ----------
    schema_path : Path
        Path to feature_schema.yaml
        
    Attributes
    ----------
    schema : dict
        Loaded feature schema (families, aliases, units)
    required_features : list
        List of required canonical feature names
    alias_map : dict
        Mapping from extractor names to canonical names
    """
    
    def __init__(self, schema_path: Path = Path("config/feature_schema.yaml")):
        """Initialize normalizer with feature schema."""
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.required_features = self._extract_required_features()
        self.alias_map = self._build_alias_map()
        
        logger.info(f"FlowNormalizer initialized: {len(self.required_features)} required features")
    
    def _load_schema(self) -> dict:
        """
        Load feature schema from YAML.
        
        Returns
        -------
        dict
            Feature schema
            
        Raises
        ------
        ConfigError
            If schema file missing or invalid
        """
        if not self.schema_path.exists():
            raise ConfigError(f"Feature schema not found: {self.schema_path}")
        
        try:
            with open(self.schema_path, 'r') as f:
                schema = yaml.safe_load(f)
            
            if not schema or 'families' not in schema:
                raise ConfigError("Invalid feature schema: 'families' key missing")
            
            return schema
        except Exception as e:
            raise ConfigError(f"Failed to load feature schema: {e}")
    
    def _extract_required_features(self) -> list:
        """
        Extract list of required canonical feature names from schema.
        
        Returns
        -------
        list
            Required feature names
        """
        required = []
        
        for family in self.schema.get('families', []):
            for feature in family.get('features', []):
                if feature.get('required', True):  # Default to required
                    required.append(feature['canonical_name'])
        
        return required
    
    def _build_alias_map(self) -> Dict[str, str]:
        """
        Build mapping from extractor column names to canonical names.
        
        Returns
        -------
        dict
            Mapping {extractor_name: canonical_name}
        """
        alias_map = {}
        
        for family in self.schema.get('families', []):
            for feature in family.get('features', []):
                canonical = feature['canonical_name']
                
                # Add canonical name as identity mapping
                alias_map[canonical] = canonical
                
                # Add aliases
                for alias in feature.get('aliases', []):
                    alias_map[alias] = canonical
        
        logger.debug(f"Built alias map: {len(alias_map)} mappings")
        return alias_map
    
    def normalize(
        self,
        df: pd.DataFrame,
        extractor_name: str = "CICFlowMeter"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Normalize extractor output to canonical schema.
        
        Parameters
        ----------
        df : pd.DataFrame
            Raw extractor output (e.g., CICFlowMeter CSV)
        extractor_name : str
            Name of extractor (for logging)
            
        Returns
        -------
        features : pd.DataFrame
            Canonical feature DataFrame (model input)
        metadata : pd.DataFrame
            Metadata DataFrame (five-tuple, timestamps, flow IDs)
            
        Raises
        ------
        SchemaMismatchError
            If required features are missing or invalid
        """
        logger.info(f"Normalizing {len(df)} flows from {extractor_name}")
        logger.debug(f"Input columns: {len(df.columns)}")
        
        # Step 1: Separate metadata
        metadata = self._extract_metadata(df)
        
        # Step 2: Apply column aliases
        df_aliased = self._apply_aliases(df)
        
        # Step 3: Apply unit conversions
        df_converted = self._apply_conversions(df_aliased)
        
        # Step 4: Calculate derived features
        df_derived = self._calculate_derived(df_converted)
        
        # Step 5: Select canonical features only
        features = self._select_canonical_features(df_derived)
        
        # Step 6: Validate schema compliance
        self._validate_schema(features)
        
        logger.info(f"Normalization complete: {len(features.columns)} canonical features")
        
        return features, metadata
    
    def _extract_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract metadata columns (five-tuple, timestamps, IDs).
        
        Parameters
        ----------
        df : pd.DataFrame
            Raw extractor output
            
        Returns
        -------
        pd.DataFrame
            Metadata columns
        """
        metadata_cols = []
        
        # Common metadata column patterns
        metadata_patterns = [
            'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol',
            'src', 'dst', 'sport', 'dport', 'proto',
            'timestamp', 'flow_id', 'flow_start', 'flow_end'
        ]
        
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in metadata_patterns):
                metadata_cols.append(col)
        
        if metadata_cols:
            logger.debug(f"Extracted {len(metadata_cols)} metadata columns")
            return df[metadata_cols].copy()
        else:
            logger.debug("No metadata columns found")
            return pd.DataFrame(index=df.index)
    
    def _apply_aliases(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns using alias map.
        
        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame
            
        Returns
        -------
        pd.DataFrame
            DataFrame with canonical column names
        """
        # Build rename mapping (only for columns that exist)
        rename_map = {}
        for col in df.columns:
            if col in self.alias_map:
                canonical = self.alias_map[col]
                if canonical != col:  # Only rename if different
                    rename_map[col] = canonical
        
        if rename_map:
            logger.debug(f"Renaming {len(rename_map)} columns")
            df = df.rename(columns=rename_map)
        
        return df
    
    def _apply_conversions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply unit conversions per schema.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with aliased columns
            
        Returns
        -------
        pd.DataFrame
            DataFrame with converted units
        """
        # Conversions specified in schema (e.g., seconds → milliseconds)
        conversions = self.schema.get('conversions', {})
        
        for col in df.columns:
            if col in conversions:
                conversion = conversions[col]
                df[col] = df[col] * conversion.get('factor', 1.0)
                logger.debug(f"Converted {col}: factor={conversion.get('factor')}")
        
        return df
    
    def _calculate_derived(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived features from base features.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with base features
            
        Returns
        -------
        pd.DataFrame
            DataFrame with derived features added
        """
        # Example derived features (add as needed per schema)
        
        # Flow bytes per packet (if base features present)
        if 'flow_bytes_fwd' in df and 'flow_packets_fwd' in df:
            df['flow_bytes_per_packet_fwd'] = (
                df['flow_bytes_fwd'] / df['flow_packets_fwd'].replace(0, np.nan)
            )
        
        if 'flow_bytes_bwd' in df and 'flow_packets_bwd' in df:
            df['flow_bytes_per_packet_bwd'] = (
                df['flow_bytes_bwd'] / df['flow_packets_bwd'].replace(0, np.nan)
            )
        
        return df
    
    def _select_canonical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select only canonical features from DataFrame.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with mixed canonical and metadata columns
            
        Returns
        -------
        pd.DataFrame
            DataFrame with only canonical features
        """
        # Get canonical feature names that exist in df
        available_features = [col for col in df.columns if col in self.required_features]
        
        if not available_features:
            logger.warning("No canonical features found in DataFrame")
            return pd.DataFrame(index=df.index)
        
        return df[available_features].copy()
    
    def _validate_schema(self, df: pd.DataFrame):
        """
        Validate DataFrame matches canonical schema.
        
        Parameters
        ----------
        df : pd.DataFrame
            Feature DataFrame
            
        Raises
        ------
        SchemaMismatchError
            If required features are missing
        """
        missing_features = set(self.required_features) - set(df.columns)
        
        if missing_features:
            error_msg = (
                f"Schema validation failed: {len(missing_features)} required features missing.\n"
                f"Missing: {sorted(missing_features)}"
            )
            logger.error(error_msg)
            raise SchemaMismatchError(error_msg)
        
        logger.debug(f"Schema validation passed: {len(df.columns)} features present")
    
    def get_feature_info(self) -> Dict[str, Any]:
        """
        Get information about canonical feature schema.
        
        Returns
        -------
        dict
            Schema information (families, feature count, etc.)
        """
        return {
            "required_features": len(self.required_features),
            "families": len(self.schema.get('families', [])),
            "alias_mappings": len(self.alias_map),
            "schema_path": str(self.schema_path)
        }
