# Demo Fallback Plans & Troubleshooting

**Purpose:** Emergency procedures for viva demo when primary systems fail.  
**Last Updated:** 2026-10-11

---

## Quick Reference

| Problem | Page | Quick Fix |
|---------|------|-----------|
| Environment broken | [§1](#1-environment-issues) | Use pre-captured screenshots |
| Dashboard won't start | [§2](#2-dashboard-issues) | Open static HTML or PNG plots |
| Models missing | [§3](#3-registry-issues) | Show artifacts directly |
| Packet Tracer fails | [§4](#4-packet-tracer-issues) | Use topology diagram |
| Commands fail | [§5](#5-command-failures) | Show artifact files |
| Time pressure | [§6](#6-time-constraints) | Use condensed 10-min script |

---

## 1. Environment Issues

### Problem: Python environment broken, libraries missing

**Symptoms:**
```
ModuleNotFoundError: No module named 'pandas'
ImportError: cannot import name 'load_config'
```

### Fallback Actions

#### Option A: Use Pre-Captured Artifacts

**What to Show:**
1. **Model Comparison Table:**
   - File: `artifacts/reports/comparison.csv`
   - Open in Excel or Notepad
   - Read results aloud

2. **Metrics JSON:**
   - File: `artifacts/runs/xgboost_20261014_012230/metrics.json`
   - Show in text editor
   - Explain structure

3. **Confusion Matrix:**
   - File: `artifacts/reports/xgboost_20261014_012230/confusion_matrix.png`
   - Open in image viewer

**Script:**

> "Due to an environment issue, I'll demonstrate using the saved artifacts. These are the actual results from model evaluation, stored in JSON and CSV format for reproducibility. Here's the comparison showing XGBoost achieved 98.12% test accuracy..."

#### Option B: Code Walkthrough

**What to Show:**
1. Open `models/xgboost_model.py` in text editor
2. Explain model architecture:
   ```python
   XGBClassifier(
       n_estimators=100,
       max_depth=6,
       learning_rate=0.1,
       ...
   )
   ```
3. Show preprocessing pipeline in `preprocessing/pipeline.py`
4. Explain anti-leakage guards

**Script:**

> "Let me walk through the code implementation. Here's our XGBoost model definition with hyperparameter search space. The pipeline ensures preprocessing is fitted only on training data..."

#### Option C: Documentation Review

**What to Show:**
1. `docs/task_reports/CN-010.md` (Evaluation results)
2. `docs/decisions/best_model.md` (XGBoost selection)
3. `files/TRD.md` (Technical design)

**Script:**

> "I'll reference our evaluation report. Section 2 shows test results: XGBoost 98.12% accuracy, Decision Tree 96.70%, Random Forest 96.47%, SVM 70.10%. The decision record explains why XGBoost was selected based on CV macro-F1..."

### Prevention

**Before Demo:**
```powershell
# Test environment
python scripts/verify_environment.py

# If broken, reinstall
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 2. Dashboard Issues

### Problem: Dashboard won't start (port conflict, encoding errors)

**Symptoms:**
```
OSError: [WinError 10048] Address already in use
UnicodeEncodeError: 'charmap' codec can't encode character
```

### Fallback Actions

#### Option A: Use Static Plots

**What to Show:**
1. **Comparison Chart:**
   - File: `artifacts/reports/comparison.png`
   - Open in image viewer or PowerPoint

2. **Feature Importance:**
   - File: `artifacts/runs/random_forest_*/feature_importances.png` (if exists)
   - Or create slide from data

3. **Confusion Matrices:**
   - Files: `artifacts/reports/*/confusion_matrix.png`

**Script:**

> "The dashboard isn't running, but here are the key visualizations. This chart compares our four models. XGBoost leads with 98.12% accuracy. This feature importance plot shows timing features (IAT) dominate classification..."

#### Option B: Open Static HTML

**What to Do:**
1. Navigate to `dashboard/templates/index.html`
2. Right-click → Open with → Browser
3. Limited interactivity, but shows structure

**Limitation:** No data loading, only template visible

**Script:**

> "Here's the dashboard HTML template. In a working session, this displays live data from artifact files. The tabs organize information: Overview, Dataset, Models, Features, and Network topology."

#### Option C: Manual Data Presentation

**What to Show:**
1. Open `data/processed/split_manifest.json`:
   ```json
   {
     "train_samples": 47696,
     "test_samples": 11925,
     "classes": ["Web", "VoIP", "Streaming", "FTP"]
   }
   ```

2. Read comparison CSV in Excel

**Script:**

> "Let me show the raw data files. This manifest shows 59,621 total flows, 80/20 train/test split. The comparison CSV has all model metrics..."

### Workaround: Fix Dashboard

**If time permits:**

```powershell
# Fix encoding issue
$env:PYTHONIOENCODING = "utf-8"

# Kill process on port 5000
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force

# Restart dashboard
python -m dashboard.app
```

---

## 3. Registry Issues

### Problem: Model registry empty or corrupted

**Symptoms:**
```
No registered models found
RegistryIntegrityError: Checksum mismatch
```

### Fallback Actions

#### Option A: Show Run Directories

**What to Do:**
1. Navigate to `artifacts/runs/`
2. List available runs:
   - `decision_tree_20261014_011743/`
   - `xgboost_20261014_012230/`
   - `random_forest_20261014_012003/`
   - `svm_20261014_014253/`

3. Open `xgboost_20261014_012230/summary.json`:
   ```json
   {
     "run_id": "xgboost_20261014_012230",
     "model_name": "xgboost",
     "cv_macro_f1": 0.9629,
     "test_accuracy": 0.9812,
     "test_macro_f1": 0.9716
   }
   ```

**Script:**

> "The registry isn't loading, but the model artifacts are intact. Here's the XGBoost run directory with all results. The summary JSON shows 98.12% test accuracy, 97.16% macro F1..."

#### Option B: Regenerate Registry

**If time permits:**

```powershell
# Register best model
python -m models.registry register --run-id xgboost_20261014_012230 --model-name "XGBoost Best"

# List registry
python -m models.registry list
```

---

## 4. Packet Tracer Issues

### Problem: Packet Tracer not installed, topology missing, or crashes

**Symptoms:**
- Software not found
- `.pkt` file missing
- Devices not connecting

### Fallback Actions

#### Option A: Use Topology Diagram

**What to Show:**
1. Open `docs/NETWORK_TOPOLOGY.md`
2. Show network diagram (text or draw on board)
3. Explain topology verbally

**Network Structure:**
```
         Internet
             |
         [Router R1]
        /           \
   [Switch SW1]    [Servers]
       |               |
   [4 Clients]    [4 Servers]
```

**Script:**

> "Here's the network topology diagram. We have 4 clients generating different traffic types: PC-Web, PC-VoIP, PC-Stream, PC-FTP. Each connects to a corresponding server through router R1. This setup simulates a real enterprise network..."

#### Option B: Traffic Characteristics Table

**Show on slides or board:**

| Traffic | IAT Pattern | Packet Size | Behavior |
|---------|-------------|-------------|----------|
| **Web** | Variable (high variance) | 200-800 B | Bursty |
| **VoIP** | Constant (~20ms) | 160-200 B | Regular |
| **Streaming** | Medium variance | 800-1400 B | Sustained |
| **FTP** | Minimal (1-5ms) | 1400-1500 B | Bulk |

**Script:**

> "Without live simulation, I'll explain the traffic characteristics. VoIP needs constant low-latency delivery, so packets arrive every 20ms with small size. Web browsing is bursty — request, pause, read, request again — creating high IAT variance. FTP maximizes throughput with back-to-back maximum-size packets..."

#### Option C: Wireshark/PCAP Visualization

**If sample PCAP available:**
1. Open PCAP in Wireshark
2. Show packet list
3. Filter by conversation (tcp.stream eq 0)
4. Show IO graph (Statistics → IO Graph)

**Script:**

> "Here's real captured traffic visualized in Wireshark. Notice the packet timing patterns — this bursty pattern indicates web traffic, while this constant stream is VoIP..."

### Quick Rebuild (if time permits)

**From `QUICK_START_PACKET_TRACER.md`:**
1. Drag 1 Router, 1 Switch, 8 PCs (10 min)
2. Configure IPs (5 min)
3. Test connectivity (1 min)

---

## 5. Command Failures

### Problem: CLI commands fail or hang

**Symptoms:**
```
python -m evaluation.evaluate --run-id <id>
# Hangs or errors
```

### Fallback Actions

#### Strategy: Show Pre-Computed Results

**Instead of running commands, show outputs:**

1. **Evaluation Results:**
   - File: `docs/task_reports/CN-010.md`
   - Contains all evaluation outputs

2. **Comparison Results:**
   - File: `artifacts/reports/comparison.md`
   - Formatted report with tables

3. **Registry Listing:**
   - File: `artifacts/registry/registry.json`
   - Manual inspection in text editor

**Script:**

> "I'll show the pre-computed results instead of running live commands. Here's the evaluation report from CN-010, showing all four models evaluated on the test set..."

---

## 6. Time Constraints

### Problem: Demo cut short (only 10 minutes available)

### Condensed Demo Script

**Total: 10 minutes**

#### Minute 1: Introduction

> "FlowSentry classifies network traffic using ML on flow-level timing features, without payload inspection. Best model: XGBoost, 98.12% accuracy."

#### Minutes 2-3: Show Results (Priority #1)

**Dashboard → Models tab OR comparison.csv**

> "Four models trained: Decision Tree (96.70%), Random Forest (96.47%), SVM (70.10% — subsample), XGBoost (98.12% — best). XGBoost selected by cross-validation macro-F1. Test accuracy exceeds Review-1 benchmark."

#### Minutes 4-5: Features (Priority #2)

**Dashboard → Features tab OR feature importance chart**

> "We extract 79 flow features from packet timing and size patterns. After selection, 9 features remain. Timing features (IAT) dominate. VoIP has constant IAT, Web is bursty, Streaming is sustained, FTP is bulk."

#### Minutes 6-7: Dataset (Priority #3)

> "ISCX-VPN2016 dataset: 59,621 flows, 4 classes (Web, VoIP, Streaming, FTP), 80/20 train/test split. Preprocessing: imputation, min-max scaling, feature selection. Anti-leakage: all preprocessing fitted on training only, test set never touched during training."

#### Minute 8: Pipeline (Priority #4)

> "Pipeline: Packets → five-tuple grouping → bidirectional flow → feature extraction → preprocessing → ML model → class prediction. Works with encrypted traffic because timing patterns visible regardless of encryption."

#### Minute 9: Limitations

> "Limitations: PCAP pipeline not delivered (Npcap dependency), live classification not implemented (optional), SVM trained on subsample (scalability). Future work: deploy live system, test on additional datasets."

#### Minute 10: Questions

> "Thank you! Questions?"

### What to Skip in Short Demo

- ❌ Packet Tracer simulation (nice-to-have)
- ❌ CLI demonstrations (show artifacts instead)
- ❌ Detailed preprocessing steps (brief summary)
- ❌ SVM scalability deep-dive (mention briefly)
- ❌ Dashboard navigation (show one key chart)

---

## 7. Known Issues & Workarounds

### Issue 1: Demo Script Unicode Error

**Problem:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'
```

**Cause:** `scripts/demo.py` uses emoji characters, Windows terminal uses cp1252

**Workaround:**
```powershell
$env:PYTHONIOENCODING = "utf-8"
python scripts/demo.py
```

**Alternative:** Don't use `scripts/demo.py` in viva — use Dashboard or manual artifact presentation

---

### Issue 2: Old Model Evaluation Fails

**Problem:**
```
ValueError: Feature names should match... Unnamed: 0 missing
```

**Cause:** Old models trained before preprocessing fix

**Workaround:**
- Only evaluate recent models (after 2026-10-14 01:22)
- Use these run IDs:
  - `xgboost_20261014_012230` ✅
  - `decision_tree_20261014_011743` ✅
  - `random_forest_20261014_012003` ✅
  - `svm_20261014_014253` ✅

**Don't Use:** `decision_tree_20261014_010406` (old, deprecated)

---

## 8. Emergency Contact Sheet

### If All Fails: Presentation-Only Mode

**Materials to Prepare:**
1. PowerPoint with key charts (comparison table, feature importance)
2. Printed topology diagram
3. Code snippets in slides (model definition, pipeline)
4. Key numbers on index cards (98.12%, 9 features, 59,621 flows)

**Script Structure:**
1. Introduction (problem, solution)
2. Show topology diagram (explain traffic types)
3. Explain flow features (IAT concept)
4. Show results slides (comparison table)
5. Conclusion (achievements, limitations)

**Practice:** Memorize key numbers and concepts

---

## 9. Pre-Demo Checklist Expanded

### 1 Hour Before

- [ ] Test environment: `python scripts/verify_environment.py`
- [ ] Test dashboard: `python -m dashboard.app` → open http://localhost:5000
- [ ] Test registry: `python -m models.registry list`
- [ ] Open Packet Tracer, load topology, test connectivity
- [ ] Charge laptop (!)
- [ ] Close unnecessary applications

### 30 Minutes Before

- [ ] Run condensed demo dry-run (10 min version)
- [ ] Screenshot working dashboard (backup)
- [ ] Print topology diagram (paper backup)
- [ ] Prepare fallback materials (artifact files open in folders)
- [ ] Test projector connection

### 5 Minutes Before

- [ ] Final connectivity test
- [ ] Dashboard running
- [ ] Browser tabs open (dashboard, backup artifacts)
- [ ] Packet Tracer ready (or topology diagram)
- [ ] Notes/index cards ready

---

## 10. Artifacts Quick Reference

### Essential Files for Demo

**Model Results:**
- `artifacts/reports/comparison.csv` — All model metrics
- `artifacts/reports/comparison.png` — Performance chart
- `artifacts/reports/comparison.md` — Formatted report

**Best Model (XGBoost):**
- `artifacts/runs/xgboost_20261014_012230/summary.json` — Overview
- `artifacts/runs/xgboost_20261014_012230/metrics.json` — Detailed metrics
- `artifacts/reports/xgboost_20261014_012230/confusion_matrix.png` — Confusion matrix

**Dataset:**
- `data/processed/split_manifest.json` — Dataset statistics

**Documentation:**
- `docs/task_reports/CN-010.md` — Evaluation results
- `docs/decisions/best_model.md` — XGBoost selection
- `docs/DEMO.md` — Full demo script

### File Locations

```
artifacts/
├── reports/
│   ├── comparison.csv         ← Show in Excel
│   ├── comparison.png         ← Show in image viewer
│   └── xgboost_*/
│       └── confusion_matrix.png
├── runs/
│   └── xgboost_20261014_012230/
│       ├── summary.json       ← Key metrics
│       └── metrics.json       ← Detailed results
└── registry/
    └── registry.json          ← Model registry

docs/
├── DEMO.md                    ← Full script
├── demo_fallbacks.md          ← This file
├── NETWORK_TOPOLOGY.md        ← Topology diagram
└── task_reports/
    └── CN-010.md              ← Evaluation report
```

---

## 11. Stress Management

### If Everything Goes Wrong

**Remember:**
1. **You know the material** — You built this system
2. **Show what works** — Artifacts exist even if live demo fails
3. **Explain conceptually** — Viva tests understanding, not demo skills
4. **Stay calm** — Acknowledge issue, move to fallback smoothly

**Phrases to Use:**

> "The live demo isn't working, but I can show the pre-computed results..."

> "Let me walk through the code implementation instead..."

> "I'll explain the concept using this diagram..."

### Deep Breath Checklist

- [ ] Pause, breathe
- [ ] State the issue briefly
- [ ] Choose fallback (artifacts, code, or conceptual)
- [ ] Continue confidently
- [ ] Answer questions fully

---

## 12. Post-Mortem Template

**After Demo, Document Issues:**

**What Went Wrong:**
- [ ] Environment issue (specify)
- [ ] Dashboard failed (reason)
- [ ] Packet Tracer issue
- [ ] Time constraint
- [ ] Other:

**Fallback Used:**
- [ ] Pre-captured artifacts
- [ ] Code walkthrough
- [ ] Documentation review
- [ ] Conceptual explanation
- [ ] Condensed script

**What Worked Well:**
- 

**Improvements for Next Time:**
- 

---

**End of Fallback Guide**

**Remember:** The goal is to demonstrate understanding, not perfect execution. Fallbacks are legitimate alternatives. Good luck! 🎓
