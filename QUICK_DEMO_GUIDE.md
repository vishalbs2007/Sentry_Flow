# FlowSentry - Quick Demo Guide

## 🚀 Run the Demo (Choose One)

### Option 1: Interactive (Recommended for first time)
```powershell
powershell -ExecutionPolicy Bypass -File COMPLETE_DEMO.ps1
```
- Pauses at each step
- Press Enter to continue
- ~3 minutes total

### Option 2: Automated (Quick verification)
```powershell
powershell -ExecutionPolicy Bypass -File COMPLETE_DEMO_AUTO.ps1
```
- No pauses, runs straight through
- ~30 seconds total

## 📊 What You'll See

```
✅ Model Comparison - 98.12% accuracy (XGBoost)
✅ Test Data Loading - 11,925 flows
✅ Live Classification - 100 random samples
✅ Predictions Table - True vs Predicted
✅ Confusion Matrix - Visual breakdown
✅ Summary Metrics - 99% accuracy on demo
```

## 🎯 Expected Results

**Overall**: 96-99% accuracy (varies by random sample)

**Per-Class**:
- File Transfer: ~100%
- VoIP: ~100%
- Web Browsing: ~100%
- Streaming: ~89-100%

**Output**: `artifacts/demo_results.csv` (detailed predictions)

## ⚡ One-Liner Demo

```powershell
# Quick demo with results
powershell -ExecutionPolicy Bypass -File COMPLETE_DEMO_AUTO.ps1 ; type artifacts\demo_results.csv | Select-Object -First 20
```

## 📖 Full Documentation

- **DEMO_README.md** - Complete usage guide
- **DEMO_SUMMARY.md** - Technical details & achievements
- **SOLUTION.md** - Full project documentation
- **NS2_INTEGRATION_GUIDE.md** - NS2 integration details

## 🔧 Troubleshooting

**Problem**: "Cannot find file"  
**Solution**: `cd D:\Sentry_Flow`

**Problem**: "Module not found"  
**Solution**: `.\.venv\Scripts\Activate.ps1`

**Problem**: Want different samples?  
**Solution**: Edit script, change `random_state=42` to any number

## 🎥 For Live Presentation

1. **Setup** (5 seconds): Open PowerShell in project root
2. **Run**: `powershell -ExecutionPolicy Bypass -File COMPLETE_DEMO.ps1`
3. **Narrate** as each section appears:
   - Part 1: "We trained 4 models, XGBoost won with 98%"
   - Part 2: "Loading 11,925 test flows"
   - Part 3: "Classifying 100 random samples..."
   - Part 4: "99% accuracy! Only 1 mistake"
   - Part 5: "Confusion matrix shows excellent separation"
   - Part 6: "Full pipeline working end-to-end"

**Total time**: 3 minutes

## ✨ Key Talking Points

1. **High Accuracy**: 98.12% on full test set, 99% on demo sample
2. **Real Classification**: Actual predictions on real network flows
3. **4 Traffic Types**: Web, VoIP, Streaming, File Transfer
4. **Production Ready**: Complete pipeline with validation
5. **NS2 Compatible**: Can process NS2 simulation traces

## 📦 Project Status

✅ Training Complete - 98.12% accuracy  
✅ Testing Complete - All metrics validated  
✅ Classification Working - 99% on samples  
✅ NS2 Integration - Conversion functional  
✅ Demo Ready - Interactive + Automated  

**Status**: 🎉 **READY FOR DEMONSTRATION**

---

## Quick Commands Cheat Sheet

```powershell
# Run interactive demo
.\COMPLETE_DEMO.ps1

# Run automated demo
.\COMPLETE_DEMO_AUTO.ps1

# View results
type artifacts\demo_results.csv

# Show all model metrics
.\show_results.ps1

# NS2 integration test
python -m simulation.ns2.validate

# Classify custom PCAP
python -m inference.pcap_classifier --pcap file.pcap
```

---

**Questions?** See DEMO_README.md or DEMO_SUMMARY.md
