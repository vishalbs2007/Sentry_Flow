"""
flow/cicflowmeter_adapter.py
----------------------------
Adapter for CICFlowMeter flow feature extractor (CN-013).

Wraps CICFlowMeter command-line tool following the FlowExtractor protocol.
Uses subprocess with argument list (no shell=True) for security.

Verified Implementation (docs/verification/cicflowmeter.md):
- Tool: cicflowmeter (Python package from GitHub)
- Version: 0.4.2 (hieulw/cicflowmeter master)
- Runtime: Python 3.11+
- Command: cicflowmeter -f <input.pcap> -c <output.csv>
- Features: 83 flow-level features

⚠️ REQUIRES: Npcap driver + WinDump.exe (tcpdump for Windows)

FALLBACK: If CICFlowMeter fails (missing WinDump), automatically falls back
to pure-Python Scapy extractor with reduced feature set.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from common.errors import ExtractionError, ExtractorUnavailableError
from common.logging_setup import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class CICFlowMeterAdapter:
    """
    Adapter for CICFlowMeter tool.
    
    Implements FlowExtractor protocol using subprocess to call
    the cicflowmeter command-line tool.
    
    Parameters
    ----------
    command_path : str | None
        Path to cicflowmeter executable. If None, auto-detect from virtualenv.
    timeout : int
        Timeout in seconds for extraction (default: 300 = 5 minutes)
        
    Attributes
    ----------
    command : list
        Command list for subprocess (e.g., ['cicflowmeter'])
    timeout : int
        Extraction timeout in seconds
        
    Raises
    ------
    ExtractionError
        If cicflowmeter cannot be found or is not working
    """
    
    def __init__(self, command_path: str | None = None, timeout: int = 300):
        """Initialize CICFlowMeter adapter."""
        self.timeout = timeout
        
        # Auto-detect or use provided command
        if command_path is None:
            self.command = self._detect_command()
        else:
            self.command = [command_path]
        
        # Verify command works
        self._verify_installation()
        
        logger.info(f"CICFlowMeter adapter initialized: {' '.join(self.command)}")
    
    def _detect_command(self) -> list:
        """
        Auto-detect cicflowmeter command.
        
        Tries:
        1. cicflowmeter.exe in virtualenv Scripts/
        2. python -m cicflowmeter
        
        Returns
        -------
        list
            Command list for subprocess
            
        Raises
        ------
        ExtractionError
            If cicflowmeter cannot be found
        """
        # Try .exe in Scripts
        venv_exe = Path(sys.executable).parent / "cicflowmeter.exe"
        if venv_exe.exists():
            logger.debug(f"Found cicflowmeter.exe: {venv_exe}")
            return [str(venv_exe)]
        
        # Try python -m
        try:
            result = subprocess.run(
                [sys.executable, "-m", "cicflowmeter", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.debug("Found cicflowmeter via python -m")
                return [sys.executable, "-m", "cicflowmeter"]
        except Exception as e:
            logger.debug(f"python -m cicflowmeter failed: {e}")
        
        raise ExtractionError(
            "CICFlowMeter not found. Install: pip install git+https://github.com/hieulw/cicflowmeter.git"
        )
    
    def _verify_installation(self):
        """
        Verify cicflowmeter can run.
        
        Raises
        ------
        ExtractionError
            If verification fails
        """
        try:
            result = subprocess.run(
                self.command + ["--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise ExtractionError(
                    f"CICFlowMeter returned non-zero: {result.returncode}\n{result.stderr}"
                )
            logger.debug("CICFlowMeter verification passed")
        except subprocess.TimeoutExpired:
            raise ExtractionError("CICFlowMeter --help timed out")
        except FileNotFoundError:
            raise ExtractionError(f"CICFlowMeter command not found: {self.command[0]}")
        except Exception as e:
            raise ExtractionError(f"CICFlowMeter verification failed: {e}")
    
    def extract_flows(
        self,
        pcap_path: Path,
        output_path: Path | None = None
    ) -> pd.DataFrame:
        """
        Extract flow features from PCAP using CICFlowMeter.
        
        Parameters
        ----------
        pcap_path : Path
            Path to input PCAP file
        output_path : Path, optional
            Path to save CSV (if None, use temporary file)
            
        Returns
        -------
        pd.DataFrame
            Flow features (one row per flow)
            
        Raises
        ------
        FileNotFoundError
            If pcap_path doesn't exist
        ExtractionError
            If extraction fails
        """
        # Validate input
        if not pcap_path.exists():
            raise FileNotFoundError(f"PCAP file not found: {pcap_path}")
        
        logger.info(f"Extracting flows from: {pcap_path}")
        
        # Determine output path
        use_temp = output_path is None
        if use_temp:
            temp_dir = tempfile.mkdtemp(prefix="cicflowmeter_")
            output_path = Path(temp_dir) / "flows.csv"
        
        # Build command: cicflowmeter -f input.pcap -c output.csv
        command = self.command + [
            "-f", str(pcap_path),
            "-c", str(output_path)
        ]
        
        logger.debug(f"Running: {' '.join(command)}")
        logger.debug(f"Timeout: {self.timeout}s")
        
        # Execute CICFlowMeter
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Log output
            if result.stdout:
                logger.debug(f"CICFlowMeter stdout: {result.stdout}")
            if result.stderr:
                logger.debug(f"CICFlowMeter stderr: {result.stderr}")
            
            # Check exit code
            if result.returncode != 0:
                error_msg = f"CICFlowMeter failed (exit {result.returncode})"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                
                # Check for common errors
                if "tcpdump is not available" in result.stderr:
                    logger.warning("CICFlowMeter failed: tcpdump/WinDump not available")
                    logger.warning("Falling back to pure-Python Scapy extractor...")
                    
                    # Use Scapy fallback
                    try:
                        from flow.scapy_extractor import ScapyFlowExtractor
                        logger.info(f"Using Scapy extractor as fallback")
                        
                        extractor = ScapyFlowExtractor()
                        temp_output_dir = Path(tempfile.mkdtemp(prefix="scapy_extract_"))
                        csv_path = extractor.extract(pcap_path, temp_output_dir)
                        df = pd.read_csv(csv_path)
                        
                        # Clean up
                        csv_path.unlink()
                        temp_output_dir.rmdir()
                        
                        logger.info(f"Scapy extractor: {len(df)} flows with {len(df.columns)} features (simplified)")
                        return df
                        
                    except ImportError as import_err:
                        error_msg += f"\n\n⚠️ Npcap driver + WinDump not installed."
                        error_msg += f"\n   Download from: https://npcap.com/"
                        error_msg += f"\n   See: WINDUMP_SOLUTION.md for setup instructions"
                        error_msg += f"\n\nFallback extractor also unavailable: {import_err}"
                        raise ExtractionError(error_msg)
                    except Exception as fallback_err:
                        error_msg += f"\n\nFallback Scapy extractor also failed: {fallback_err}"
                        raise ExtractionError(error_msg)
                else:
                    raise ExtractionError(error_msg)
            
            # Check output was created
            if not output_path.exists():
                raise ExtractionError(
                    f"CICFlowMeter did not create output file: {output_path}"
                )
            
            # Load DataFrame
            df = pd.read_csv(output_path)
            logger.info(f"Extracted {len(df)} flows with {len(df.columns)} features")
            
            # Clean up temp file if used
            if use_temp:
                output_path.unlink()
                Path(temp_dir).rmdir()
                logger.debug("Cleaned up temporary files")
            
            return df
            
        except subprocess.TimeoutExpired:
            error_msg = f"CICFlowMeter timed out after {self.timeout}s"
            logger.error(error_msg)
            raise ExtractionError(error_msg)
        
        except pd.errors.EmptyDataError:
            logger.warning(f"CICFlowMeter produced empty CSV for {pcap_path}")
            # Return empty DataFrame with expected structure
            return pd.DataFrame()
        
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            error_msg = f"Unexpected error during extraction: {e}"
            logger.exception(error_msg)
            raise ExtractionError(error_msg)
    
    def get_extractor_info(self) -> Dict[str, Any]:
        """
        Get CICFlowMeter metadata.
        
        Returns
        -------
        dict
            Extractor information (name, version, features, etc.)
        """
        # Try to get version
        try:
            import cicflowmeter
            version = getattr(cicflowmeter, '__version__', 'unknown')
        except ImportError:
            version = "unknown"
        
        return {
            "name": "CICFlowMeter",
            "version": version,
            "feature_count": 83,  # Per verification
            "implementation": "Python (hieulw/cicflowmeter GitHub master)",
            "command": " ".join(self.command),
            "timeout": self.timeout,
            "requirements": ["Npcap driver (https://npcap.com/)"]
        }
    
    def __repr__(self) -> str:
        """String representation."""
        info = self.get_extractor_info()
        return f"CICFlowMeterAdapter(version={info['version']}, features={info['feature_count']})"

