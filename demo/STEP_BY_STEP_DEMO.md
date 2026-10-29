# FlowSentry - Step-by-Step Demo Guide

## Overview

This guide provides **4 separate commands** to demonstrate the complete ML pipeline. Each command can be run independently and shows a specific part of the system.

```
Step 1: Traffic Data       → Shows network flows to be classified
Step 2: Model Accuracy      → Shows trained model performance
Step 3: Classification      → Runs model on test data (the main demo!)
Step 4: Detailed Results    → In-depth analysis with confusion matrix
```

---

## Prerequisites

### 1. Navigate to Project Directory
```powershell
cd D:\Sentry_Flow
```

### 2. Activate Python Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` in your prompt.

---

## Step 1: Show Traffic Data

**Purpose**: Verify we have network traffic data ready for classification

### Command
```powershell
powershell -ExecutionPolicy Bypass -File demo\step1_show_traffic.ps1
```

### What You'll See
- ✅ NS2 simulation script (if available)
- ✅ Test dataset location and size (11,925 flows)
- ✅ Sample network flows with features
- ✅ Traffic type distribution

### Expected Output
```
================================================================================
  STEP 1: NETWORK TRAFFIC DATA
================================================================================

[OK] NS2 Simulation Script Found
  File: flowsentry.tcl

Production Test Data:
  Source: ISCX-VPN2016 Dataset (Scenario B)
  Location: data\processed\test\test.csv
  Total Flows: 11925

Sample Network Flows (first 5):
     duration  total_fiat  total_biat  flowPktsPerSecond  target_class
0    29997247      259056    19105861            0.23335  Web Browsing
1    24800969         204      480102            0.40321  File Transfer
...

Traffic Type Distribution:
Web Browsing     6831
File Transfer    2324
VoIP             1904
Streaming         866
```

### Interpretation
- **11,925 flows**: Our test dataset size
- **4 classes**: Web Browsing, File Transfer, VoIP, Streaming
- **Duration, FIAT, BIAT**: Key features used by ML model

---

## Step 2: Show Model Accuracy

**Purpose**: Display performance metrics of trained models

### Command
```powershell
powershell -ExecutionPolicy Bypass -File demo\step2_model_accuracy.ps1
```

### What You'll See
- ✅ Comparison of all 4 trained models
- ✅ Best model selection (XGBoost 98.12%)
- ✅ Per-class F1 scores
- ✅ Training dataset details

### Expected Output
```
================================================================================
  STEP 2: MODEL TRAINING RESULTS
================================================================================

MODEL COMPARISON (All Trained Models):

Model         Accuracy Macro F1 Precision Recall
-----         -------- -------- --------- ------
XGBOOST       98.12%   97.16%   97.24%    97.16%
DECISION_TREE 96.70%   95.77%   95.87%    95.77%
RANDOM_FOREST 96.47%   95.65%   95.85%    95.65%
SVM           70.10%   65.37%   70.28%    65.37%

[WINNER] XGBOOST selected with 98.12% accuracy

PER-CLASS PERFORMANCE (Best Model):

Traffic Type    F1 Score
------------    --------
File Transfer   96.85%
Streaming       94.82%
VoIP            99.49%
Web Browsing    98.18%

TRAINING DETAILS:
  Dataset: ISCX-VPN2016 (Scenario B)
  Training Samples: 47,696 flows
  Test Samples: 11,925 flows
  Features: 21 CICFlowMeter-compatible features
  Classes: 4 (Web, VoIP, Streaming, File Transfer)
```

### Interpretation
- **98.12% accuracy**: XGBoost is our best model
- **VoIP best**: 99.49% F1 score (easiest to classify)
- **Streaming hardest**: 94.82% F1 (similar to web browsing)

---

## Step 3: Classify Traffic (Main Demo!)

**Purpose**: Run real-time classification on 100 test samples

### Command
```powershell
powershell -ExecutionPolicy Bypass -File demo\step3_classify_traffic.ps1
```

### What You'll See
- ✅ Model loading
- ✅ Feature extraction (21 features)
- ✅ Real-time classification progress
- ✅ Sample predictions with confidence
- ✅ Per-class accuracy breakdown
- ✅ Confusion matrix preview

### Expected Output
```
================================================================================
  STEP 3: TRAFFIC CLASSIFICATION
================================================================================

Loading trained model...
  Model: Decision Tree
  Location: artifacts\registry\decision_tree_20261014_011743\

Preparing test data...
  Loading 100 random flows from test set
  Extracting 21 features per flow

================================================================================
CLASSIFICATION IN PROGRESS
================================================================================

[1/5] Loading test data...
      Loaded 11,925 total flows
      Selected 100 random samples

[2/5] Loading trained model...
      Model expects 21 features

[3/5] Preparing features...
      Feature matrix: (100, 21)

[4/5] Running classification...
      Classified 100 flows

[5/5] Saving results...
      Saved to: demo/classification_results.csv

================================================================================
CLASSIFICATION COMPLETE
================================================================================

Samples Classified: 100
Overall Accuracy:   99.00%
Correct:            99
Incorrect:          1

SAMPLE PREDICTIONS (First 10):
--------------------------------------------------------------------------------
True Class           Predicted            Result     Confidence
--------------------------------------------------------------------------------
VoIP                 VoIP                 CORRECT      100.0%
Streaming            Web Browsing         WRONG         77.3%
File Transfer        File Transfer        CORRECT       95.2%
VoIP                 VoIP                 CORRECT      100.0%
Web Browsing         Web Browsing         CORRECT       89.1%
File Transfer        File Transfer        CORRECT       95.2%
Web Browsing         Web Browsing         CORRECT       89.1%
File Transfer        File Transfer        CORRECT       95.2%
VoIP                 VoIP                 CORRECT      100.0%
Web Browsing         Web Browsing         CORRECT       89.1%

PER-CLASS ACCURACY:
--------------------------------------------------------------------------------
  File Transfer         33/ 33 (100.0%)
  Streaming              8/  9 ( 88.9%)
  VoIP                  16/ 16 (100.0%)
  Web Browsing          42/ 42 (100.0%)

CONFUSION MATRIX DATA:
--------------------------------------------------------------------------------
True \ Predicted    File Transfe     Streaming          VoIP  Web Browsing
--------------------------------------------------------------------------------
File Transfer                 33             0             0             0
Streaming                      0             8             0             1
VoIP                           0             0            16             0
Web Browsing                   0             0             0            42

[OK] Classification complete!
```

### Interpretation
- **99% accuracy**: Excellent performance on this sample
- **1 error**: Streaming → Web Browsing (common confusion)
- **VoIP perfect**: 100% accuracy (distinctive traffic pattern)
- **Results saved**: `demo\classification_results.csv`

---

## Step 4: Detailed Results Analysis

**Purpose**: In-depth analysis with visual confusion matrix and error analysis

### Command
```powershell
powershell -ExecutionPolicy Bypass -File demo\step4_view_results.ps1
```

### What You'll See
- ✅ Overall performance summary
- ✅ Per-class breakdown with ratings
- ✅ Detailed predictions table
- ✅ Full confusion matrix (color-coded)
- ✅ Misclassified examples analysis

### Expected Output
```
================================================================================
  STEP 4: DETAILED RESULTS ANALYSIS
================================================================================

[OK] Loaded 100 predictions

================================================================================
  OVERALL PERFORMANCE
================================================================================

Total Samples:     100
Correct:           99 (99.00%)
Incorrect:         1 (1.00%)

================================================================================
  PER-CLASS BREAKDOWN
================================================================================

File Transfer        33 /33  (100.0%) [EXCELLENT]
Streaming             8 /9   ( 88.9%) [GOOD]
VoIP                 16 /16  (100.0%) [EXCELLENT]
Web Browsing         42 /42  (100.0%) [EXCELLENT]

================================================================================
  SAMPLE PREDICTIONS (First 15)
================================================================================

True Class       Predicted        Result  Confidence
----------       ---------        ------  ----------
VoIP             VoIP             OK      100.0%
Streaming        Web Browsing     WRONG    77.3%
File Transfer    File Transfer    OK       95.2%
VoIP             VoIP             OK      100.0%
Web Browsing     Web Browsing     OK       89.1%
...

================================================================================
  CONFUSION MATRIX
================================================================================
Rows = True Class, Columns = Predicted Class

True \ Predicted    File Transfe     Streaming          VoIP  Web Browsing
--------------------------------------------------------------------------------
File Transfer                 33             0             0             0
Streaming                      0             8             0             1
VoIP                           0             0            16             0
Web Browsing                   0             0             0            42

================================================================================
  MISCLASSIFIED EXAMPLES
================================================================================

Total misclassifications: 1

True Class       Predicted As     Confidence
----------       ------------     ----------
Streaming        Web Browsing     77.3%

Note: These edge cases show where the model needs improvement

================================================================================
  ANALYSIS COMPLETE
================================================================================

Key Findings:
  [*] Overall accuracy: 99.00%
  [*] Best performing: File Transfer (100.0%)
  [*] Results saved: demo\classification_results.csv

[OK] All demo steps completed successfully!
```

### Interpretation
- **Green diagonal**: Correct classifications (33+8+16+42 = 99)
- **Red off-diagonal**: Misclassifications (1 Streaming→Web)
- **Excellent ratings**: 3 out of 4 classes at 100%
- **Edge case**: 1 Streaming flow confused with Web Browsing

---

## Quick Reference - All Commands

```powershell
# Step 1: Show traffic data
powershell -ExecutionPolicy Bypass -File demo\step1_show_traffic.ps1

# Step 2: Show model accuracy
powershell -ExecutionPolicy Bypass -File demo\step2_model_accuracy.ps1

# Step 3: Classify traffic (main demo)
powershell -ExecutionPolicy Bypass -File demo\step3_classify_traffic.ps1

# Step 4: View detailed results
powershell -ExecutionPolicy Bypass -File demo\step4_view_results.ps1
```

---

## Complete Demo Run (Copy & Paste)

Run all steps in sequence:

```powershell
# Full demo sequence
cd D:\Sentry_Flow
.\.venv\Scripts\Activate.ps1

# Step 1
powershell -ExecutionPolicy Bypass -File demo\step1_show_traffic.ps1
Read-Host "Press Enter to continue to Step 2"

# Step 2
powershell -ExecutionPolicy Bypass -File demo\step2_model_accuracy.ps1
Read-Host "Press Enter to continue to Step 3"

# Step 3
powershell -ExecutionPolicy Bypass -File demo\step3_classify_traffic.ps1
Read-Host "Press Enter to continue to Step 4"

# Step 4
powershell -ExecutionPolicy Bypass -File demo\step4_view_results.ps1
```

---

## Output Files

After running the demo, you'll have:

```
demo/
├── classification_results.csv   # Detailed predictions with probabilities
├── step1_show_traffic.ps1       # Traffic data script
├── step2_model_accuracy.ps1     # Model metrics script
├── step3_classify_traffic.ps1   # Classification script
└── step4_view_results.ps1       # Analysis script
```

### View Results CSV
```powershell
# First 20 rows
Get-Content demo\classification_results.csv | Select-Object -First 20

# Open in Excel
Start-Process demo\classification_results.csv

# Count correct predictions
(Import-Csv demo\classification_results.csv | Where-Object {$_.Correct -eq "True"}).Count
```

---

## Troubleshooting

### Error: "Cannot find file"
**Solution**: Make sure you're in the project root
```powershell
cd D:\Sentry_Flow
```

### Error: "Python not found"
**Solution**: Activate virtual environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Error: "Classification results not found" (Step 4)
**Solution**: Run Step 3 first
```powershell
powershell -ExecutionPolicy Bypass -File demo\step3_classify_traffic.ps1
```

### Want different random samples?
Edit `demo\step3_classify_traffic.ps1`, find this line:
```python
test_sample = test_data.sample(n=100, random_state=42)
```
Change `random_state=42` to any other number (e.g., `random_state=99`)

---

## Performance Expectations

### Typical Results (may vary slightly due to random sampling)

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| Overall Accuracy | 96-99% | Usually ~99% |
| File Transfer | 98-100% | Very distinctive pattern |
| VoIP | 99-100% | Best performing class |
| Web Browsing | 98-100% | Clear patterns |
| Streaming | 85-95% | Sometimes confused with Web |

### Common Confusions
1. **Streaming ↔ Web Browsing** (most common)
   - Reason: Similar traffic patterns (HTTP-based)
   - Model confidence: Usually 70-85%

2. **File Transfer ↔ Web Browsing** (rare)
   - Reason: Large file downloads via HTTP
   - Model confidence: Usually 60-80%

---

## For Presentations

### 5-Minute Demo Script

```
[1 min] Step 1: "Here's our network traffic data - 11,925 real flows"
[1 min] Step 2: "We trained 4 models, XGBoost achieved 98% accuracy"
[2 min] Step 3: "Watch it classify 100 flows in real-time - 99% accurate!"
[1 min] Step 4: "Confusion matrix shows only 1 error out of 100"
```

### Key Talking Points
- ✅ Real network traffic (ISCX-VPN2016 dataset)
- ✅ Production-ready ML pipeline
- ✅ 98.12% accuracy on 11,925 test samples
- ✅ 4 traffic types classified
- ✅ VoIP detection nearly perfect (99.49%)
- ✅ Fast classification (~30 seconds for 100 flows)

---

## Next Steps

### After Demo
1. Review results CSV in Excel
2. Try different random samples
3. Classify custom PCAP files
4. Explore NS2 integration

### Custom Classification
```powershell
# Classify your own PCAP file
python -m inference.pcap_classifier --pcap path\to\your\capture.pcap
```

### NS2 Simulation
```powershell
# Run NS2 traffic simulation
powershell -File simulation\ns2\run_ns2.ps1
```

---

## Success Criteria Checklist

After running all 4 steps, verify:

- [ ] Step 1: Shows 11,925 test flows
- [ ] Step 2: XGBoost listed as best model (98.12%)
- [ ] Step 3: Classification completes with >95% accuracy
- [ ] Step 4: Confusion matrix shows diagonal dominance
- [ ] All 4 classes represented in sample
- [ ] Results CSV created successfully
- [ ] No errors during execution

---

## Support

### Documentation
- `DEMO_README.md` - Detailed usage guide
- `DEMO_SUMMARY.md` - Technical achievements
- `SOLUTION.md` - Complete project documentation
- `NS2_INTEGRATION_GUIDE.md` - NS2 integration details

### Questions?
Check the main documentation files or review the PowerShell scripts in the `demo/` folder.

---

**Demo Ready!** 🚀 Run the commands above to see FlowSentry in action.
