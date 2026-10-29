# FlowSentry Demo - Quick Command Reference

## 🚀 Run All 4 Steps

```powershell
cd D:\Sentry_Flow
.\.venv\Scripts\Activate.ps1

# Step 1: Traffic Data
powershell -ExecutionPolicy Bypass -File demo\step1_show_traffic.ps1

# Step 2: Model Accuracy  
powershell -ExecutionPolicy Bypass -File demo\step2_model_accuracy.ps1

# Step 3: Classification (Main Demo!)
powershell -ExecutionPolicy Bypass -File demo\step3_classify_traffic.ps1

# Step 4: Detailed Results
powershell -ExecutionPolicy Bypass -File demo\step4_view_results.ps1
```

## 📊 What Each Command Shows

| Step | Command | Shows | Time |
|------|---------|-------|------|
| 1 | `step1_show_traffic.ps1` | 11,925 network flows | ~10s |
| 2 | `step2_model_accuracy.ps1` | 98.12% accuracy (XGBoost) | ~5s |
| 3 | `step3_classify_traffic.ps1` | **99% on 100 samples** ⭐ | ~30s |
| 4 | `step4_view_results.ps1` | Confusion matrix + analysis | ~10s |

## 🎯 Expected Results

```
Step 1: Shows 11,925 test flows with traffic distribution
Step 2: XGBoost at 98.12%, VoIP best at 99.49%
Step 3: 99 correct, 1 wrong (Streaming→Web confusion)
Step 4: Full confusion matrix, all classes >88% accuracy
```

## 📁 Output File

```powershell
# After Step 3, view results:
demo\classification_results.csv
```

## ✅ Success Criteria

- [ ] Step 1 loads 11,925 flows
- [ ] Step 2 shows 98.12% accuracy
- [ ] Step 3 achieves >95% accuracy
- [ ] Step 4 shows confusion matrix
- [ ] Results CSV created

---

**Full Guide**: `demo/COMPLETE_DEMONSTRATION_GUIDE.md`
