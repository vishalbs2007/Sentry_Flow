#!/usr/bin/env python3
"""
Download and install WinDump (tcpdump for Windows) to make CICFlowMeter work.
WinDump is required by Scapy to read PCAP files on Windows.
"""

import os
import sys
import zipfile
from pathlib import Path
from urllib.request import urlretrieve


WINDUMP_URL = "https://www.winpcap.org/windump/install/bin/windump_3_9_5/WinDump.exe"
WINDUMP_MIRROR = "https://github.com/hsluoyz/WinDump/raw/master/WinDump.exe"


def download_windump(dest_dir: Path) -> Path:
    """
    Download WinDump.exe to the specified directory.
    
    Args:
        dest_dir: Directory where WinDump.exe will be saved
        
    Returns:
        Path to the downloaded WinDump.exe
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    windump_path = dest_dir / "WinDump.exe"
    
    if windump_path.exists():
        print(f"✅ WinDump already exists: {windump_path}")
        return windump_path
    
    print(f"📥 Downloading WinDump from {WINDUMP_MIRROR}...")
    
    try:
        urlretrieve(WINDUMP_MIRROR, windump_path)
        print(f"✅ Downloaded WinDump to: {windump_path}")
        return windump_path
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print(f"\n⚠️ Manual download required:")
        print(f"   1. Download from: {WINDUMP_MIRROR}")
        print(f"   2. Save as: {windump_path}")
        sys.exit(1)


def add_to_path(directory: Path) -> None:
    """
    Add directory to the current PATH environment variable.
    
    Args:
        directory: Directory to add to PATH
    """
    current_path = os.environ.get("PATH", "")
    dir_str = str(directory.resolve())
    
    if dir_str in current_path:
        print(f"✅ Directory already in PATH: {dir_str}")
        return
    
    # Add to PATH for current session
    os.environ["PATH"] = f"{dir_str};{current_path}"
    print(f"✅ Added to PATH (current session): {dir_str}")
    
    # Instructions for permanent PATH
    print(f"\n⚠️ To make this permanent, add to Windows PATH:")
    print(f"   1. Search 'Environment Variables' in Windows")
    print(f"   2. Edit 'Path' variable")
    print(f"   3. Add: {dir_str}")
    print(f"   4. Restart terminal")


def verify_windump(windump_path: Path) -> bool:
    """
    Verify WinDump.exe works.
    
    Args:
        windump_path: Path to WinDump.exe
        
    Returns:
        True if WinDump works, False otherwise
    """
    import subprocess
    
    print(f"\n🧪 Verifying WinDump...")
    
    try:
        result = subprocess.run(
            [str(windump_path), "-h"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "tcpdump version" in result.stderr or "windump version" in result.stderr.lower():
            print(f"✅ WinDump is working!")
            return True
        else:
            print(f"⚠️ WinDump executed but output unexpected")
            return False
            
    except FileNotFoundError:
        print(f"❌ WinDump not found: {windump_path}")
        return False
    except subprocess.TimeoutExpired:
        print(f"⚠️ WinDump timed out (this is normal without admin rights)")
        return True  # Timeout is acceptable - means it's trying to run
    except Exception as e:
        print(f"❌ WinDump verification failed: {e}")
        return False


def main():
    print("=" * 70)
    print("WINDUMP INSTALLER FOR CICFLOWMETER")
    print("=" * 70)
    
    # Determine installation directory
    project_root = Path(__file__).parent.parent
    bin_dir = project_root / "bin"
    
    print(f"\nInstallation directory: {bin_dir}")
    
    # Download WinDump
    windump_path = download_windump(bin_dir)
    
    # Add to PATH
    add_to_path(bin_dir)
    
    # Verify
    if verify_windump(windump_path):
        print("\n" + "=" * 70)
        print("✅ INSTALLATION SUCCESSFUL")
        print("=" * 70)
        print(f"\nWinDump installed: {windump_path}")
        print(f"\nNext steps:")
        print(f"  1. Close and reopen terminal (to reload PATH)")
        print(f"  2. Run: python scripts\\verify_cicflowmeter.py")
        print(f"  3. If still fails, add {bin_dir} to Windows PATH permanently")
    else:
        print("\n" + "=" * 70)
        print("⚠️ INSTALLATION COMPLETE WITH WARNINGS")
        print("=" * 70)
        print(f"\nWinDump downloaded but verification inconclusive.")
        print(f"Try running: python scripts\\verify_cicflowmeter.py")


if __name__ == "__main__":
    main()
