# WinDump Installation Guide for CICFlowMeter

## Problem

CICFlowMeter requires `tcpdump` (or `WinDump.exe` on Windows) to read PCAP files. When it's missing, you get:

```
scapy.error.Scapy_Exception: tcpdump is not available
```

## Solution Options

### Option 1: Install WinDump (Recommended)

**Step 1: Download WinDump**

Download from one of these sources:

1. **Official (May be outdated):**
   - https://www.winpcap.org/windump/install/default.htm
   - Direct link: https://www.winpcap.org/windump/install/bin/windump_3_9_5/WinDump.exe

2. **Alternative Mirror:**
   - https://www.tcpdump.org/
   - Search for "Windows port" or "WinDump"

3. **Npcap SDK (Includes WinDump):**
   - https://npcap.com/#download
   - Download "Npcap SDK" (not just Npcap installer)
   - Extract and find `WinDump.exe` in the SDK folder

**Step 2: Place WinDump.exe**

Save `WinDump.exe` to one of these locations:

```powershell
# Option A: Project bin directory (recommended)
d:\Sentry_Flow\bin\WinDump.exe

# Option B: Python Scripts directory
d:\Sentry_Flow\.venv\Scripts\WinDump.exe

# Option C: System directory (requires admin)
C:\Windows\System32\WinDump.exe
```

**Step 3: Add to PATH (if using Option A)**

```powershell
# Temporary (current session only)
$env:PATH = "d:\Sentry_Flow\bin;$env:PATH"

# Verify
Get-Command WinDump.exe
```

**Step 4: Verify**

```powershell
cd d:\Sentry_Flow
.venv\Scripts\Activate.ps1
python scripts\verify_cicflowmeter.py
```

---

### Option 2: Use Alternative Flow Extractor (Bypass CICFlowMeter)

If WinDump installation fails, use a pure-Python flow extractor instead.

**Create a bypass adapter:**

```powershell
cd d:\Sentry_Flow
.venv\Scripts\Activate.ps1

# Install additional dependencies
pip install dpkt
```

I'll create this alternative implementation if needed.

---

### Option 3: Use Pre-extracted Features (Demo Only)

For demonstration purposes, you can use pre-extracted flow features without needing CICFlowMeter.

**Steps:**

1. Use existing processed datasets in `data/processed/`
2. Load trained model from registry
3. Run inference on CSV features (not PCAP)

**Command:**

```powershell
python -m inference.batch_classifier --features data/processed/test.csv --output artifacts/demo
```

---

## Current Status

- ✅ Npcap installed (packet capture driver)
- ❌ WinDump missing (PCAP file reader)
- ✅ CICFlowMeter installed (Python package)

**Needed:** WinDump.exe to bridge CICFlowMeter → PCAP files

---

## Quick Fix (Try First)

### Download WinDump Manually

1. **Download from Npcap SDK:**
   ```
   https://npcap.com/#download
   → Click "Npcap SDK" (not "Npcap Installer")
   → Download the ZIP file
   ```

2. **Extract the ZIP:**
   - Open the downloaded ZIP file
   - Navigate to `wpcap/bin/` or similar
   - Find `WinDump.exe` (may be named `tcpdump.exe`)

3. **Copy to project:**
   ```powershell
   # Create bin directory if it doesn't exist
   New-Item -ItemType Directory -Force -Path d:\Sentry_Flow\bin
   
   # Copy WinDump.exe to bin
   Copy-Item <path_to_downloaded>\WinDump.exe d:\Sentry_Flow\bin\
   ```

4. **Add to PATH and verify:**
   ```powershell
   $env:PATH = "d:\Sentry_Flow\bin;$env:PATH"
   WinDump.exe -h
   ```

5. **Test CICFlowMeter:**
   ```powershell
   cd d:\Sentry_Flow
   .venv\Scripts\Activate.ps1
   python scripts\verify_cicflowmeter.py
   ```

---

## Alternative: Use Wireshark's tshark

If you have Wireshark installed, `tshark.exe` can serve as a tcpdump replacement.

**Steps:**

1. **Verify Wireshark/tshark is installed:**
   ```powershell
   Get-Command tshark
   # Usually in: C:\Program Files\Wireshark\tshark.exe
   ```

2. **Create symbolic link:**
   ```powershell
   # Run as Administrator
   cd d:\Sentry_Flow\bin
   New-Item -ItemType SymbolicLink -Name "tcpdump.exe" -Target "C:\Program Files\Wireshark\tshark.exe"
   ```

3. **Add to PATH:**
   ```powershell
   $env:PATH = "d:\Sentry_Flow\bin;$env:PATH"
   ```

4. **Test:**
   ```powershell
   tcpdump.exe --version
   python scripts\verify_cicflowmeter.py
   ```

---

## Troubleshooting

### Error: "WinDump.exe is not recognized"

**Cause:** WinDump not in PATH

**Fix:**
```powershell
# Check if file exists
Test-Path d:\Sentry_Flow\bin\WinDump.exe

# Add to PATH
$env:PATH = "d:\Sentry_Flow\bin;$env:PATH"

# Verify
Get-Command WinDump.exe
```

### Error: "tcpdump is not available" (still happens)

**Cause:** Scapy can't find tcpdump/WinDump

**Fix 1 - Rename file:**
```powershell
# Scapy looks for "tcpdump.exe" on Windows
cd d:\Sentry_Flow\bin
Copy-Item WinDump.exe tcpdump.exe
```

**Fix 2 - Configure Scapy:**
```python
# Add to common/config.py or create common/scapy_config.py
import scapy.config
scapy.config.conf.prog.tcpdump = r"d:\Sentry_Flow\bin\WinDump.exe"
```

### Error: "WinDump requires Npcap"

**Cause:** WinDump needs packet capture driver

**Fix:** Npcap already installed, restart computer

---

## What You Can Do Right Now

### Without WinDump (Current State)

You can still demonstrate:

1. **ML Pipeline:**
   ```powershell
   python -m models.train decision_tree
   python -m evaluation.evaluate
   python -m evaluation.compare
   ```

2. **Dashboard:**
   ```powershell
   python -m dashboard.app
   ```

3. **Test Suite:**
   ```powershell
   pytest -v
   ```

4. **Inference on CSV (not PCAP):**
   ```powershell
   # Load test features directly (bypass PCAP extraction)
   python -c "
   from models.registry import load_active_model
   import pandas as pd
   
   model = load_active_model()
   features = pd.read_csv('data/processed/test.csv')
   predictions = model.predict(features)
   print(predictions)
   "
   ```

### After WinDump Installation

Full PCAP pipeline:
```powershell
python scripts\generate_test_pcap.py
python -m inference.pcap_classifier --pcap data/sample/test_traffic.pcap --output artifacts/test
```

---

## Next Steps

**Priority 1: Get WinDump** (5-10 minutes)

Try these in order:

1. ✅ Download Npcap SDK, extract WinDump.exe
2. ✅ Copy to `d:\Sentry_Flow\bin\WinDump.exe`
3. ✅ Add to PATH: `$env:PATH = "d:\Sentry_Flow\bin;$env:PATH"`
4. ✅ Verify: `python scripts\verify_cicflowmeter.py`

**Priority 2: Demo Without PCAP** (if WinDump fails)

Focus on:
- ML training results (98.12% accuracy)
- Dashboard visualization
- Model comparison
- Existing evaluation metrics

**Priority 3: Packet Tracer** (2-3 hours, optional)

Build network topology for enhanced demo.

---

## Summary

**Problem:** CICFlowMeter needs WinDump (tcpdump for Windows) to read PCAP files.

**Solution:** Download WinDump.exe and place it in project's `bin/` directory.

**Workaround:** If WinDump unavailable, demonstrate ML pipeline without PCAP classification.

**Current Blocker:** Need WinDump.exe from Npcap SDK or Wireshark installation.

---

**Status:** Awaiting WinDump installation to complete PCAP pipeline testing.
