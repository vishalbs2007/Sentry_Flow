"""
tests/unit/test_cicflowmeter_adapter.py
---------------------------------------
Unit tests for CICFlowMeter adapter (CN-013).

Tests command construction, timeout handling, error cases.
Uses mocked subprocess to avoid requiring actual cicflowmeter installation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import subprocess
import pandas as pd

from flow.cicflowmeter_adapter import CICFlowMeterAdapter
from common.errors import FlowExtractionError


class TestCICFlowMeterAdapter:
    """Tests for CICFlowMeterAdapter."""
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_detect_command_finds_exe(self, mock_exists, mock_run):
        """Test command detection finds cicflowmeter.exe in virtualenv."""
        # Mock .exe exists
        mock_exists.return_value = True
        
        # Mock --help succeeds
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")
        
        adapter = CICFlowMeterAdapter()
        
        # Should use .exe path
        assert adapter.command[0].endswith("cicflowmeter.exe")
        
        # Verification should have been called
        mock_run.assert_called_once()
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_detect_command_falls_back_to_module(self, mock_exists, mock_run):
        """Test command detection falls back to python -m."""
        # Mock .exe doesn't exist
        mock_exists.return_value = False
        
        # Mock python -m succeeds
        def run_side_effect(cmd, *args, **kwargs):
            if "--help" in cmd:
                return Mock(returncode=0, stderr="", stdout="")
            raise Exception("Unexpected command")
        
        mock_run.side_effect = run_side_effect
        
        adapter = CICFlowMeterAdapter()
        
        # Should use python -m
        assert adapter.command == [pytest.mock.ANY, "-m", "cicflowmeter"]
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_verify_installation_fails_on_nonzero(self, mock_exists, mock_run):
        """Test verification fails if --help returns non-zero."""
        mock_exists.return_value = True
        
        # Mock --help fails
        mock_run.return_value = Mock(returncode=1, stderr="Error", stdout="")
        
        with pytest.raises(FlowExtractionError, match="returned non-zero"):
            CICFlowMeterAdapter()
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_verify_installation_fails_on_timeout(self, mock_exists, mock_run):
        """Test verification fails if --help times out."""
        mock_exists.return_value = True
        
        # Mock --help times out
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=10)
        
        with pytest.raises(FlowExtractionError, match="timed out"):
            CICFlowMeterAdapter()
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    @patch('flow.cicflowmeter_adapter.pd.read_csv')
    def test_extract_flows_success(self, mock_read_csv, mock_path_exists, mock_run):
        """Test successful flow extraction."""
        # Mock adapter initialization
        def exists_side_effect(path=None):
            # .exe exists, PCAP exists, output exists
            return True
        mock_path_exists.side_effect = exists_side_effect
        
        # Mock --help succeeds
        # Mock extraction succeeds
        def run_side_effect(cmd, *args, **kwargs):
            if "--help" in cmd:
                return Mock(returncode=0, stderr="", stdout="")
            elif "-f" in cmd:
                return Mock(returncode=0, stderr="", stdout="Extraction complete")
            raise Exception(f"Unexpected command: {cmd}")
        
        mock_run.side_effect = run_side_effect
        
        # Mock DataFrame
        mock_df = pd.DataFrame({'flow_id': [1, 2], 'src_ip': ['1.1.1.1', '2.2.2.2']})
        mock_read_csv.return_value = mock_df
        
        adapter = CICFlowMeterAdapter()
        
        # Extract flows
        pcap_path = Path("test.pcap")
        result = adapter.extract_flows(pcap_path)
        
        # Should return DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        
        # Should have called subprocess with correct args
        extraction_call = [call for call in mock_run.call_args_list if "-f" in call[0][0]]
        assert len(extraction_call) == 1
        assert "-f" in extraction_call[0][0][0]
        assert "-c" in extraction_call[0][0][0]
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_extract_flows_handles_npcap_error(self, mock_path_exists, mock_run):
        """Test extraction detects Npcap missing error."""
        # Mock initialization
        def exists_side_effect(path=None):
            return True
        mock_path_exists.side_effect = exists_side_effect
        
        # Mock extraction fails with Npcap error
        def run_side_effect(cmd, *args, **kwargs):
            if "--help" in cmd:
                return Mock(returncode=0, stderr="", stdout="")
            elif "-f" in cmd:
                return Mock(
                    returncode=1,
                    stderr="tcpdump is not available",
                    stdout=""
                )
            raise Exception(f"Unexpected command")
        
        mock_run.side_effect = run_side_effect
        
        adapter = CICFlowMeterAdapter()
        
        pcap_path = Path("test.pcap")
        
        with pytest.raises(FlowExtractionError, match="Npcap"):
            adapter.extract_flows(pcap_path)
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_extract_flows_handles_timeout(self, mock_path_exists, mock_run):
        """Test extraction handles timeout."""
        # Mock initialization
        mock_path_exists.return_value = True
        
        # Mock extraction times out
        def run_side_effect(cmd, *args, **kwargs):
            if "--help" in cmd:
                return Mock(returncode=0, stderr="", stdout="")
            elif "-f" in cmd:
                raise subprocess.TimeoutExpired(cmd=cmd, timeout=300)
            raise Exception(f"Unexpected command")
        
        mock_run.side_effect = run_side_effect
        
        adapter = CICFlowMeterAdapter(timeout=300)
        
        pcap_path = Path("test.pcap")
        
        with pytest.raises(FlowExtractionError, match="timed out after 300s"):
            adapter.extract_flows(pcap_path)
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_extract_flows_file_not_found(self, mock_path_exists, mock_run):
        """Test extraction raises FileNotFoundError for missing PCAP."""
        # Mock initialization (adapter exists)
        call_count = [0]
        
        def exists_side_effect(path=None):
            call_count[0] += 1
            if call_count[0] <= 2:  # First 2 calls are for initialization
                return True
            return False  # PCAP doesn't exist
        
        mock_path_exists.side_effect = exists_side_effect
        
        # Mock --help succeeds
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")
        
        adapter = CICFlowMeterAdapter()
        
        pcap_path = Path("nonexistent.pcap")
        
        with pytest.raises(FileNotFoundError, match="not found"):
            adapter.extract_flows(pcap_path)
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    @patch('flow.cicflowmeter_adapter.pd.read_csv')
    def test_extract_flows_handles_empty_output(self, mock_read_csv, mock_path_exists, mock_run):
        """Test extraction handles empty CSV (no flows)."""
        mock_path_exists.return_value = True
        
        # Mock extraction succeeds but produces empty CSV
        def run_side_effect(cmd, *args, **kwargs):
            if "--help" in cmd:
                return Mock(returncode=0, stderr="", stdout="")
            elif "-f" in cmd:
                return Mock(returncode=0, stderr="", stdout="")
            raise Exception(f"Unexpected command")
        
        mock_run.side_effect = run_side_effect
        
        # Mock empty DataFrame
        mock_read_csv.side_effect = pd.errors.EmptyDataError("no data")
        
        adapter = CICFlowMeterAdapter()
        
        pcap_path = Path("empty.pcap")
        result = adapter.extract_flows(pcap_path)
        
        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_get_extractor_info(self, mock_exists, mock_run):
        """Test get_extractor_info returns metadata."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")
        
        adapter = CICFlowMeterAdapter()
        
        info = adapter.get_extractor_info()
        
        assert info["name"] == "CICFlowMeter"
        assert "version" in info
        assert info["feature_count"] == 83
        assert "implementation" in info
        assert "command" in info
        assert "Npcap" in info["requirements"][0]
    
    @patch('flow.cicflowmeter_adapter.subprocess.run')
    @patch('flow.cicflowmeter_adapter.Path.exists')
    def test_repr(self, mock_exists, mock_run):
        """Test __repr__ returns readable string."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0, stderr="", stdout="")
        
        adapter = CICFlowMeterAdapter()
        
        repr_str = repr(adapter)
        
        assert "CICFlowMeterAdapter" in repr_str
        assert "version" in repr_str
        assert "features=83" in repr_str


@pytest.mark.requires_cicflowmeter
class TestCICFlowMeterAdapterReal:
    """
    Real tests requiring actual cicflowmeter installation.
    
    These tests are skipped unless cicflowmeter is installed and Npcap is available.
    Run with: pytest -m requires_cicflowmeter
    """
    
    def test_real_initialization(self):
        """Test adapter initializes with real cicflowmeter."""
        try:
            adapter = CICFlowMeterAdapter()
            assert adapter.command is not None
            print(f"✅ Initialized: {adapter}")
        except FlowExtractionError as e:
            pytest.skip(f"CICFlowMeter not available: {e}")
    
    def test_real_extractor_info(self):
        """Test get_extractor_info with real installation."""
        try:
            adapter = CICFlowMeterAdapter()
            info = adapter.get_extractor_info()
            
            assert info["name"] == "CICFlowMeter"
            assert info["feature_count"] == 83
            print(f"✅ Extractor info: {info}")
        except FlowExtractionError as e:
            pytest.skip(f"CICFlowMeter not available: {e}")
