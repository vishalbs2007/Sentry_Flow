"""
tests/integration/test_pcap_flow_extraction.py
----------------------------------------------
Integration tests for PCAP flow extraction pipeline (CN-014).

Tests the complete pipeline:
PCAP → CICFlowMeter → Normalizer → Canonical Features
"""

import pytest
from pathlib import Path
import pandas as pd
from unittest.mock import Mock, patch

from flow.pcap_flow_extractor import PcapFlowExtractor, extract_flows_from_pcap
from common.errors import FlowExtractionError, SchemaMismatchError


@pytest.fixture
def mock_cicflowmeter_output():
    """Mock CICFlowMeter CSV output."""
    return pd.DataFrame({
        'src_ip': ['192.168.1.100', '192.168.1.101'],
        'dst_ip': ['10.0.0.1', '10.0.0.2'],
        'src_port': [50000, 50001],
        'dst_port': [80, 443],
        'protocol': [6, 6],
        'flow_duration': [1.5, 2.3],
        'flow_iat_mean': [0.05, 0.03],
        'flow_iat_std': [0.01, 0.02],
        'fwd_packets': [10, 15],
        'bwd_packets': [8, 12],
        'fwd_bytes': [1500, 2200],
        'bwd_bytes': [1200, 1800]
    })


class TestPcapFlowExtractor:
    """Tests for PcapFlowExtractor class."""
    
    @patch('flow.pcap_flow_extractor.CICFlowMeterAdapter')
    @patch('flow.pcap_flow_extractor.FlowNormalizer')
    def test_initialization(self, mock_normalizer_class, mock_adapter_class):
        """Test extractor initializes components."""
        extractor = PcapFlowExtractor()
        
        # Should initialize adapter and normalizer
        mock_adapter_class.assert_called_once()
        mock_normalizer_class.assert_called_once()
    
    @patch('flow.pcap_flow_extractor.CICFlowMeterAdapter')
    @patch('flow.pcap_flow_extractor.FlowNormalizer')
    def test_extract_flows_success(
        self,
        mock_normalizer_class,
        mock_adapter_class,
        mock_cicflowmeter_output,
        tmp_path
    ):
        """Test successful flow extraction."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.extract_flows.return_value = mock_cicflowmeter_output
        mock_adapter.get_extractor_info.return_value = {"name": "CICFlowMeter"}
        mock_adapter_class.return_value = mock_adapter
        
        mock_normalizer = Mock()
        mock_features = pd.DataFrame({
            'flow_iat_mean': [0.05, 0.03],
            'flow_iat_std': [0.01, 0.02]
        })
        mock_metadata = pd.DataFrame({
            'src_ip': ['192.168.1.100', '192.168.1.101'],
            'dst_ip': ['10.0.0.1', '10.0.0.2']
        })
        mock_normalizer.normalize.return_value = (mock_features, mock_metadata)
        mock_normalizer.get_feature_info.return_value = {"required_features": 2}
        mock_normalizer_class.return_value = mock_normalizer
        
        # Create test PCAP
        pcap_path = tmp_path / "test.pcap"
        pcap_path.touch()
        
        # Extract flows
        extractor = PcapFlowExtractor()
        features, metadata, stats = extractor.extract_flows(pcap_path)
        
        # Verify results
        assert isinstance(features, pd.DataFrame)
        assert isinstance(metadata, pd.DataFrame)
        assert isinstance(stats, dict)
        
        assert len(features) == 2
        assert 'flow_iat_mean' in features.columns
        
        assert stats['flow_count'] == 2
        assert stats['status'] == 'success'
        
        # Verify pipeline was called
        mock_adapter.extract_flows.assert_called_once_with(pcap_path)
        mock_normalizer.normalize.assert_called_once()
    
    @patch('flow.pcap_flow_extractor.CICFlowMeterAdapter')
    @patch('flow.pcap_flow_extractor.FlowNormalizer')
    def test_extract_flows_empty_pcap(
        self,
        mock_normalizer_class,
        mock_adapter_class,
        tmp_path
    ):
        """Test extraction handles empty PCAP (no flows)."""
        # Setup mocks - adapter returns empty DataFrame
        mock_adapter = Mock()
        mock_adapter.extract_flows.return_value = pd.DataFrame()
        mock_adapter_class.return_value = mock_adapter
        
        mock_normalizer = Mock()
        mock_normalizer_class.return_value = mock_normalizer
        
        # Create test PCAP
        pcap_path = tmp_path / "empty.pcap"
        pcap_path.touch()
        
        # Extract flows
        extractor = PcapFlowExtractor()
        features, metadata, stats = extractor.extract_flows(pcap_path)
        
        # Should return empty DataFrames
        assert features.empty
        assert metadata.empty
        assert stats['flow_count'] == 0
        assert stats['status'] == 'empty'
        
        # Normalizer should not be called
        mock_normalizer.normalize.assert_not_called()
    
    @patch('flow.pcap_flow_extractor.CICFlowMeterAdapter')
    @patch('flow.pcap_flow_extractor.FlowNormalizer')
    def test_extract_flows_file_not_found(
        self,
        mock_normalizer_class,
        mock_adapter_class,
        tmp_path
    ):
        """Test extraction raises error for missing PCAP."""
        extractor = PcapFlowExtractor()
        
        nonexistent = tmp_path / "nonexistent.pcap"
        
        with pytest.raises(FileNotFoundError, match="not found"):
            extractor.extract_flows(nonexistent)
    
    @patch('flow.pcap_flow_extractor.CICFlowMeterAdapter')
    @patch('flow.pcap_flow_extractor.FlowNormalizer')
    def test_extract_flows_saves_outputs(
        self,
        mock_normalizer_class,
        mock_adapter_class,
        mock_cicflowmeter_output,
        tmp_path
    ):
        """Test extraction saves CSVs when output_dir provided."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.extract_flows.return_value = mock_cicflowmeter_output
        mock_adapter.get_extractor_info.return_value = {"name": "CICFlowMeter"}
        mock_adapter_class.return_value = mock_adapter
        
        mock_normalizer = Mock()
        mock_features = pd.DataFrame({'feature1': [1, 2]})
        mock_metadata = pd.DataFrame({'src_ip': ['1.1.1.1', '2.2.2.2']})
        mock_normalizer.normalize.return_value = (mock_features, mock_metadata)
        mock_normalizer.get_feature_info.return_value = {"required_features": 1}
        mock_normalizer_class.return_value = mock_normalizer
        
        # Create test PCAP
        pcap_path = tmp_path / "test.pcap"
        pcap_path.touch()
        
        output_dir = tmp_path / "output"
        
        # Extract flows
        extractor = PcapFlowExtractor()
        features, metadata, stats = extractor.extract_flows(pcap_path, output_dir)
        
        # Verify files were created
        assert (output_dir / "features.csv").exists()
        assert (output_dir / "metadata.csv").exists()
        assert (output_dir / "raw_features.csv").exists()
    
    @patch('flow.pcap_flow_extractor.CICFlowMeterAdapter')
    @patch('flow.pcap_flow_extractor.FlowNormalizer')
    def test_get_pipeline_info(self, mock_normalizer_class, mock_adapter_class):
        """Test get_pipeline_info returns component info."""
        mock_adapter = Mock()
        mock_adapter.get_extractor_info.return_value = {"name": "CICFlowMeter", "version": "0.4.2"}
        mock_adapter_class.return_value = mock_adapter
        
        mock_normalizer = Mock()
        mock_normalizer.get_feature_info.return_value = {"required_features": 79}
        mock_normalizer_class.return_value = mock_normalizer
        
        extractor = PcapFlowExtractor()
        info = extractor.get_pipeline_info()
        
        assert "adapter" in info
        assert "normalizer" in info
        assert info["adapter"]["name"] == "CICFlowMeter"
        assert info["normalizer"]["required_features"] == 79


class TestConvenienceFunction:
    """Tests for extract_flows_from_pcap convenience function."""
    
    @patch('flow.pcap_flow_extractor.PcapFlowExtractor')
    def test_convenience_function(self, mock_extractor_class, tmp_path):
        """Test convenience function creates extractor and calls extract_flows."""
        # Setup mock
        mock_extractor = Mock()
        mock_extractor.extract_flows.return_value = (
            pd.DataFrame({'f1': [1]}),
            pd.DataFrame({'m1': [1]}),
            {'status': 'success'}
        )
        mock_extractor_class.return_value = mock_extractor
        
        pcap_path = tmp_path / "test.pcap"
        pcap_path.touch()
        
        # Call convenience function
        features, metadata, stats = extract_flows_from_pcap(pcap_path)
        
        # Verify extractor was created and used
        mock_extractor_class.assert_called_once()
        mock_extractor.extract_flows.assert_called_once_with(pcap_path, None)
        
        assert len(features) == 1
        assert stats['status'] == 'success'


@pytest.mark.requires_cicflowmeter
class TestPcapFlowExtractionReal:
    """
    Real integration tests requiring CICFlowMeter and Npcap.
    
    Run with: pytest -m requires_cicflowmeter
    """
    
    def test_real_extraction(self, tmp_path):
        """Test real extraction with actual PCAP (if available)."""
        # This test requires:
        # 1. CICFlowMeter installed
        # 2. Npcap installed
        # 3. Sample PCAP file
        
        pytest.skip("Requires manual PCAP file and Npcap installation")
        
        # Example test structure (uncomment when ready):
        # pcap_path = Path("simulation/pcaps/sample.pcap")
        # if not pcap_path.exists():
        #     pytest.skip("Sample PCAP not found")
        # 
        # try:
        #     extractor = PcapFlowExtractor()
        #     features, metadata, stats = extractor.extract_flows(pcap_path, tmp_path)
        #     
        #     assert not features.empty
        #     assert stats['flow_count'] > 0
        #     print(f"✅ Extracted {stats['flow_count']} flows")
        # except FlowExtractionError as e:
        #     pytest.skip(f"Extraction failed: {e}")
