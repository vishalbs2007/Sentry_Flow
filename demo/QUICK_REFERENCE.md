# FlowSentry Quick Reference Card
**Essential Commands & Shortcuts**

---

## 🚀 Daily Workflow

### 1. Activate Environment
```powershell
cd d:\Sentry_Flow
.venv\Scripts\Activate.ps1
```

### 2. Verify Setup
```powershell
python scripts\verify_environment.py
python scripts\verify_cicflowmeter.py
```

### 3. Run Tests
```powershell
# All tests
pytest -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# PCAP tests (requires Npcap)
pytest -m requires_cicflowmeter -v
```

### 4. Generate Test Data
```powershell
# Create synthetic PCAP
python scripts\generate_test_pcap.py
```

### 5. Classify PCAP
```powershell
# Classify traffic
python -m inference.pcap_classifier --pcap <file.pcap> --output <output_dir>

# Example
python -m inference.pcap_classifier --pcap data/sample/test_traffic.pcap --output artifacts/results
```

### 6. Launch Dashboard
```powershell
python -m dashboard.app
# Opens browser to http://localhost:8050
```

### 7. View Results
```powershell
# CSV predictions
type artifacts\results\predictions.csv

# JSON results
type artifacts\results\predictions.json

# Summary
type artifacts\results\summary.txt
```

---

## 📊 Key File Locations

### Configuration
- `config/default.yaml` - Main config
- `config/label_mapping.yaml` - Label mappings
- `config/feature_schema.yaml` - Feature definitions
- `.env` - Environment variables (create from `.env.example`)

### Data
- `data/raw/` - Original datasets
- `data/processed/` - Cleaned data (train/test splits)
- `data/sample/` - Test PCAPs

### Models
- `artifacts/models/` - Trained model files (.joblib)
- `artifacts/registry/` - Model registry (metadata)
- `artifacts/registry/active.yaml` - Active model pointer

### Results
- `artifacts/reports/` - Evaluation reports
- `artifacts/plots/` - Visualization plots
- `artifacts/logs/` - Application logs

### Documentation
- `README.md` - Project overview
- `docs/task_reports/` - Task completion reports
- `docs/verification/` - Verification outputs
- `../DEMO_SETUP_GUIDE.md` - Setup guide

---

## 🔍 Packet Tracer Quick Setup

### Device IPs
| Device | IP Address | Gateway |
|--------|-----------|---------|
| PC-Web | 10.0.0.10 | 10.0.0.1 |
| PC-VoIP | 10.0.0.11 | 10.0.0.1 |
| PC-Stream | 10.0.0.12 | 10.0.0.1 |
| PC-FTP | 10.0.0.13 | 10.0.0.1 |
| Server-Web | 10.0.1.100 | 10.0.1.1 |
| Server-VoIP | 10.0.1.101 | 10.0.1.1 |
| Server-Stream | 10.0.1.102 | 10.0.1.1 |
| Server-FTP | 10.0.1.103 | 10.0.1.1 |
| R1 Gig0/0 | 10.0.0.1 | - |
| R1 Gig0/1 | 10.0.1.1 | - |

### Router Commands
```
enable
configure terminal
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.0
 no shutdown
 exit
interface GigabitEthernet0/1
 ip address 10.0.1.1 255.255.255.0
 no shutdown
 exit
hostname R1
end
write memory
```

### Traffic Generation
```
# Web Browsing (PC-Web)
Open Web Browser → http://10.0.1.100

# VoIP (PC-VoIP)
ping 10.0.1.101 -t

# Streaming (PC-Stream)
ping 10.0.1.102 -l 1400 -t

# FTP (PC-FTP)
ftp 10.0.1.103
User: cisco
Password: cisco
```

---

## 🧪 Testing Commands

### Verify Npcap
```powershell
python scripts\verify_cicflowmeter.py
```

### Run Specific Test
```powershell
# Test CICFlowMeter adapter
pytest tests/unit/test_cicflowmeter_adapter.py -v

# Test flow extraction
pytest tests/integration/test_pcap_flow_extraction.py -v

# Test common utilities
pytest tests/unit/test_common.py -v
```

### Run with Coverage
```powershell
pytest --cov=flow --cov=inference tests/ -v
```

---

## 📈 Model Operations

### List Registered Models
```powershell
python -c "from models.registry import list_models; print(list_models())"
```

### Get Active Model
```powershell
python -c "from models.registry import load_active_model; m = load_active_model(); print(m)"
```

### Set Active Model
```python
from models.registry import set_active_model
set_active_model("xgboost_20261024_124732")
```

---

## 🐛 Troubleshooting

### Check Python Version
```powershell
python --version
# Should be 3.9+
```

### Check Installed Packages
```powershell
pip list
```

### Check Logs
```powershell
# Latest log
Get-ChildItem artifacts\logs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content
```

### Reinstall Dependencies
```powershell
pip install -r requirements.txt --force-reinstall
```

### Clear Pytest Cache
```powershell
Remove-Item -Recurse -Force .pytest_cache
pytest --cache-clear
```

---

## 📦 Project Structure

```
Sentry_Flow/
├── capture/           # Live capture (optional)
├── common/            # Shared utilities
│   ├── config.py
│   ├── errors.py
│   ├── logging_setup.py
│   └── paths.py
├── config/            # Configuration files
├── dashboard/         # Streamlit dashboard
├── data/              # Datasets
│   ├── raw/
│   ├── processed/
│   └── sample/
├── docs/              # Documentation
├── evaluation/        # Model evaluation
├── flow/              # Flow extraction
│   ├── extractor_base.py
│   ├── cicflowmeter_adapter.py
│   ├── normalizer.py
│   └── pcap_flow_extractor.py
├── inference/         # Classification
│   └── pcap_classifier.py
├── models/            # ML models
├── preprocessing/     # Data preprocessing
├── scripts/           # Utility scripts
└── tests/             # Test suite
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 🎯 Viva Demo Flow

1. **Show Packet Tracer topology** (2 min)
   - Explain network design
   - Show device IPs
   - Demonstrate connectivity (ping)

2. **Generate traffic** (3 min)
   - Web browsing
   - VoIP (continuous ping)
   - Streaming (large packets)
   - FTP transfer

3. **Classify PCAP** (2 min)
   ```powershell
   python -m inference.pcap_classifier --pcap data/sample/test_traffic.pcap --output artifacts/demo
   ```

4. **Show results** (2 min)
   - Per-flow predictions
   - Confidence scores
   - Class distribution

5. **Dashboard** (3 min)
   ```powershell
   python -m dashboard.app
   ```
   - Model comparison
   - Feature importance
   - Confusion matrix

6. **Explain end-to-end** (3 min)
   - Network → PCAP → Features → Model → Prediction

**Total: 15 minutes**

---

## 🔗 Important Links

- **Npcap Download:** https://npcap.com/#download
- **Cisco Packet Tracer:** https://www.netacad.com/courses/packet-tracer
- **Project Documentation:** `README.md`
- **Setup Guide:** `../DEMO_SETUP_GUIDE.md`
- **Task Reports:** `docs/task_reports/`

---

## 📝 Pre-Viva Checklist

- [ ] Npcap installed and verified
- [ ] Virtual environment activated
- [ ] All tests passing
- [ ] Test PCAP generated
- [ ] PCAP classifier working
- [ ] Dashboard launches successfully
- [ ] Packet Tracer topology built and saved
- [ ] Traffic generation tested
- [ ] Demo script practiced
- [ ] Results prepared and reviewed

---

**Version:** 1.0  
**Last Updated:** 2026-10-11  
**Project:** FlowSentry - Network Traffic Classification
