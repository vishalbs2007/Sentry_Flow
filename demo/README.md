# FlowSentry Demo

## 🚀 Quick Start - 4 Simple Commands

```powershell
# Setup (once)
cd D:\Sentry_Flow
.\.venv\Scripts\Activate.ps1

# Run each step
powershell -ExecutionPolicy Bypass -File demo\step1_show_traffic.ps1
powershell -ExecutionPolicy Bypass -File demo\step2_model_accuracy.ps1
powershell -ExecutionPolicy Bypass -File demo\step3_classify_traffic.ps1
powershell -ExecutionPolicy Bypass -File demo\step4_view_results.ps1
```

## 📊 What Each Step Shows

1. **step1_show_traffic.ps1** - Shows 11,925 network flows ready for classification
2. **step2_model_accuracy.ps1** - Shows trained models (XGBoost: 98.12% accuracy)
3. **step3_classify_traffic.ps1** - **MAIN DEMO** - Classifies 100 flows (99% accuracy) ⭐
4. **step4_view_results.ps1** - Detailed analysis with confusion matrix

## 📁 Documentation

- **COMPLETE_DEMONSTRATION_GUIDE.md** - Full guide with all details
- **STEP_BY_STEP_DEMO.md** - Detailed explanation of each step
- **QUICK_COMMANDS.md** - Quick reference card

## 🎯 Expected Results

- **Overall**: 96-99% accuracy on 100 samples
- **VoIP**: 100% (perfect)
- **File Transfer**: 100% (perfect)
- **Web Browsing**: 100% (perfect)
- **Streaming**: 88-100% (sometimes confused with Web)

## 📈 Output

Results saved to: `demo\classification_results.csv`

## ✅ Success

All 4 steps should run without errors and show:
- Step 1: 11,925 flows loaded
- Step 2: XGBoost at 98.12%
- Step 3: 99% accuracy achieved
- Step 4: Confusion matrix displayed

---

**Ready to demonstrate!** 🎉
