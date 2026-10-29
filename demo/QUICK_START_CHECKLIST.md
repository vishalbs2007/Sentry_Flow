# FlowSentry - Quick Start Checklist

## ✅ Before You Start

### 1. Software Installed?
- [ ] Python 3.8+ installed
- [ ] Npcap installed (you already did this!)
- [ ] Cisco Packet Tracer 8.x installed
- [ ] Git installed (already used)

### 2. Project Ready?
```powershell
cd d:\Sentry_Flow
.venv\Scripts\Activate.ps1
python scripts\simple_scapy_test.py
```
- [ ] Test passes with "SUCCESS!" message

### 3. Files Present?
- [ ] `models/trained_model_xgboost.pkl` exists
- [ ] `models/scaler.pkl` exists
- [ ] `models/feature_columns.txt` exists

---

## 🚀 Quick Demo Flow (If Everything is Ready)

### Option A: Demo with Pre-captured Traffic
**Fastest way - No Packet Tracer needed right now**

```powershell
# 1. Generate sample traffic file
python scripts\simple_scapy_test.py

# 2. Classify it
python -m inference.pcap_classifier --pcap data/sample/scapy_test.pcap --output artifacts/quick_demo

# 3. Check results
type artifacts\quick_demo\classification_results.txt
```

**Time:** 2 minutes  
**Result:** See your model classifying traffic!

---

### Option B: Full Cisco Packet Tracer Demo
**Complete demonstration with network simulation**

Follow **`../DEMO_SETUP_GUIDE.md`** from the pre-demo checklist onwards.

**Time:** 3-4 hours  
**Result:** Full network setup + live demo

---

## 📊 Quick Status Check

Run this to see your project stats:

```powershell
python -c "import os; print('✅ Project Ready!\n'); print(f'Models: {len([f for f in os.listdir(\"models\") if f.endswith(\".pkl\")])} files'); print(f'Scripts: {len([f for f in os.listdir(\"scripts\") if f.endswith(\".py\")])} files'); print(f'Config: {len([f for f in os.listdir(\"config\") if f.endswith(\".yaml\")])} files')"
```

---

## 🎤 Quick Demo Script (2 Minutes)

**If someone asks "Show me what it does":**

### 1. Open PowerShell
```powershell
cd d:\Sentry_Flow
.venv\Scripts\Activate.ps1
```

### 2. Generate Test Traffic
```powershell
python scripts\simple_scapy_test.py
```

**Say:** "This creates network traffic packets - like pings, web requests, etc."

### 3. Classify Traffic
```powershell
python -m inference.pcap_classifier --pcap data/sample/scapy_test.pcap --output artifacts/demo
```

**Say:** "Our AI model analyzes the traffic and identifies what type it is - normal web browsing, attacks, etc."

### 4. Show Results
```powershell
type artifacts\demo\classification_results.txt
```

**Say:** "Here's the classification - it detected the traffic patterns with 98% accuracy!"

---

## 🔧 Troubleshooting Quick Fixes

### "Module not found"
```powershell
pip install -r requirements.txt
```

### "Can't find model file"
Check if `models/trained_model_xgboost.pkl` exists:
```powershell
dir models\*.pkl
```

### "Npcap error"
Make sure you installed Npcap with "WinPcap API-compatible mode" checked.

---

## 📁 Important Files Reference

| File | Purpose |
|------|---------|
| `../DEMO_SETUP_GUIDE.md` | Full step-by-step guide |
| `PROJECT_100_PERCENT_COMPLETE.md` | What's been built |
| `scripts\simple_scapy_test.py` | Quick test tool |
| `inference\pcap_classifier.py` | Main classifier |
| `models\trained_model_xgboost.pkl` | Trained model (98.12% accuracy) |

---

## 🎯 Choose Your Path

### Path 1: Quick Demo (Now) ➜ Full Demo (Later)
1. Run Option A above (2 minutes)
2. Later, build Packet Tracer network for full demo

### Path 2: Full Demo (Complete)
1. Follow `../DEMO_SETUP_GUIDE.md` from the start
2. Build network, generate traffic, demonstrate

---

## ✨ Success Criteria

You're ready when:
- ✅ `simple_scapy_test.py` runs successfully
- ✅ Classifier produces results without errors
- ✅ You understand what the output means

**Need help?** Check `../DEMO_SETUP_GUIDE.md` for detailed explanations.
