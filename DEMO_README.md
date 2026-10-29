# FlowSentry Complete Demonstration

## Overview
This demo shows the **complete end-to-end ML pipeline** working with real network traffic classification:

1. **Model Training Results** - XGBoost with 98.12% accuracy on 11,925 test samples
2. **Test Data Loading** - Load pre-processed network flows with 21 features
3. **Real-time Classification** - Classify 100 random test samples using the trained model
4. **Results & Metrics** - Show predictions, accuracy, per-class performance
5. **Confusion Matrix** - Detailed analysis of classification results

## Quick Start

### Run Interactive Demo (with pauses)
```powershell
powershell -ExecutionPolicy Bypass -File COMPLETE_DEMO.ps1
```
- Shows step-by-step progress
- Pauses at each section for you to review
- Duration: ~3 minutes

### Run Automated Demo (no pauses)
```powershell
powershell -ExecutionPolicy Bypass -File COMPLETE_DEMO_AUTO.ps1
```
- Runs completely without interaction
- Ideal for quick verification
- Duration: ~30 seconds

## What You'll See

### Part 1: Model Comparison
```
MODEL COMPARISON:
Model         Accuracy Macro F1 VoIP F1 Web F1
-----         -------- -------- ------- ------
XGBOOST       98.12%   97.16%   99.49%  98.18%
DECISION_TREE 96.70%   95.77%   98.80%  96.82%
```

### Part 2: Test Data Sample
Shows first 5 flows from 11,925 test samples with:
- Duration
- Flow inter-arrival times
- Packet statistics
- True class labels

### Part 3: Classification in Action
```
Loading trained model...
Model expects 21 features
Classifying flows...

=== CLASSIFICATION COMPLETE ===
Samples Classified: 100
Accuracy: 99.00%
Correct: 99
Incorrect: 1
```

### Part 4: Sample Predictions
```
True_Class    Predicted_Class Match Confidence
----------    --------------- ----- ----------
VoIP          VoIP            OK    100.0%    
Streaming     Web Browsing    X     0.0%      
File Transfer File Transfer   OK    0.0%      
```

### Part 5: Confusion Matrix
```
True \ Predicted       File Transfe  Streaming  VoIP  Web Browsing
--------------------------------------------------------------------------------
File Transfer                    33          0     0             0
Streaming                         0          8     0             1
VoIP                              0          0    16             0
Web Browsing                      0          0     0            42
```

### Part 6: Summary
- Training Data: 47,696 flows
- Test Data: 11,925 flows
- Test Accuracy: 98.12% (XGBoost)
- **Demo Accuracy: 99.00%** (Decision Tree on 100 samples)
- Classes: 4 (Web Browsing, VoIP, Streaming, File Transfer)
- Features: 21 selected features

## Expected Results

### Overall Performance
- **Accuracy**: ~96-99% (varies by random sample selection)
- **Most Accurate**: VoIP and Web Browsing (near 100%)
- **Occasional Confusion**: Streaming ↔ Web Browsing (similar traffic patterns)

### Per-Class Performance (typical)
- **File Transfer**: 100% accuracy
- **VoIP**: 100% accuracy
- **Web Browsing**: 100% accuracy
- **Streaming**: 88-100% accuracy

## Output Files

After running the demo, you'll find:

```
artifacts/
└── demo_results.csv          # Detailed predictions for all 100 samples
```

View results:
```powershell
type artifacts\demo_results.csv | Select-Object -First 20
```

## Technical Details

### Model Information
- **Active Model**: Decision Tree (96.70% on full test set)
- **Best Model**: XGBoost (98.12% on full test set)
- **Features Used**: 21 CICFlowMeter-compatible features
  - Duration, timing patterns, packet statistics
  - Flow inter-arrival times (min/max/mean/std)
  - Active time statistics

### Data Pipeline
1. **Raw Data**: ISCX-VPN2016 dataset (Scenario B)
2. **Preprocessing**: Feature extraction + normalization
3. **Label Mapping**: 
   - BROWSING → Web Browsing
   - VOIP → VoIP
   - STREAMING → Streaming
   - FT → File Transfer
4. **Model Training**: 80/20 train/test split
5. **Evaluation**: Classification on held-out test set

### Class Encoding
The model uses numeric labels internally:
- 0 = File Transfer
- 1 = Streaming
- 2 = VoIP
- 3 = Web Browsing

These are automatically converted to/from string labels in the demo.

## Troubleshooting

### "Cannot find file" error
Make sure you're running from the project root:
```powershell
cd D:\Sentry_Flow
```

### "Module not found" error
Activate the virtual environment first:
```powershell
.\.venv\Scripts\Activate.ps1
```

### Want to see different samples?
Edit the demo script and change the `random_state` parameter:
```python
test_sample = test_data.sample(n=100, random_state=99)  # Try different numbers
```

## Next Steps

1. **View Full Results**:
   ```powershell
   powershell -File show_results.ps1
   ```

2. **Classify Custom Traffic**:
   ```powershell
   python -m inference.pcap_classifier --pcap path/to/capture.pcap
   ```

3. **NS2 Integration**:
   ```powershell
   powershell -File simulation/ns2/run_ns2.ps1
   ```

4. **Model Comparison**:
   ```powershell
   type artifacts\reports\comparison.csv
   ```

## Demo Video Script

For presentations, follow this narrative:

1. **Hook** (10s): "Watch ML classify network traffic with 99% accuracy"
2. **Setup** (20s): Show model comparison table, explain 4 classes
3. **Load Data** (15s): Display sample flows with features
4. **Classify** (30s): Run classification, show progress
5. **Results** (45s): Walk through sample predictions, highlight accuracy
6. **Analysis** (30s): Explain confusion matrix, per-class performance
7. **Wrap** (20s): Summarize key metrics, show output files

**Total**: ~2.5 minutes

## Success Criteria

✅ Demo runs without errors  
✅ Classification accuracy > 95%  
✅ All 4 classes represented in sample  
✅ Confusion matrix shows diagonal dominance  
✅ Results file generated successfully  

---

**Questions?** Check `SOLUTION.md` for full project documentation.
