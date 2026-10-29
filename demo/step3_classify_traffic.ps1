# FlowSentry Demo - Step 3: Real-Time Classification
# Runs the trained model on test data and shows predictions

$ErrorActionPreference = "Stop"
Set-Location D:\Sentry_Flow

Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  STEP 3: TRAFFIC CLASSIFICATION" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

# Activate venv
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating Python environment..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
}

Write-Host "Loading trained model..." -ForegroundColor Yellow
Write-Host "  Model: Decision Tree" -ForegroundColor Gray
Write-Host "  Location: artifacts\registry\decision_tree_20261014_011743\" -ForegroundColor Gray
Write-Host ""

Write-Host "Preparing test data..." -ForegroundColor Yellow
Write-Host "  Loading 100 random flows from test set" -ForegroundColor Gray
Write-Host "  Extracting 21 features per flow" -ForegroundColor Gray
Write-Host ""

# Create classification script
$pythonScript = @"
import pandas as pd
import joblib
import numpy as np
import sys

print('=' * 80)
print('CLASSIFICATION IN PROGRESS')
print('=' * 80)
print()

# Load test data
print('[1/5] Loading test data...')
test_data = pd.read_csv('data/processed/test/test.csv', index_col=0)
print(f'      Loaded {len(test_data):,} total flows')

# Take sample
sample_size = 100
test_sample = test_data.sample(n=min(sample_size, len(test_data)), random_state=42)
print(f'      Selected {len(test_sample)} random samples')
print()

# Load model
print('[2/5] Loading trained model...')
pipeline = joblib.load('artifacts/registry/decision_tree_20261014_011743/pipeline.joblib')
print(f'      Model expects {len(pipeline.feature_names_in_)} features')
print()

# Define class mapping
class_mapping = {
    'File Transfer': 0,
    'Streaming': 1,
    'VoIP': 2,
    'Web Browsing': 3
}
reverse_mapping = {v: k for k, v in class_mapping.items()}

# Encode labels
print('[3/5] Preparing features...')
y_true_str = test_sample['target_class']
y_true = np.array([class_mapping[cls] for cls in y_true_str])
X_test = test_sample[pipeline.feature_names_in_]
print(f'      Feature matrix: {X_test.shape}')
print()

# Predict
print('[4/5] Running classification...')
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)
accuracy = (y_pred == y_true).mean()
print(f'      Classified {len(y_pred)} flows')
print()

# Save results
print('[5/5] Saving results...')
results_df = pd.DataFrame({
    'True_Class': [reverse_mapping[c] for c in y_true],
    'Predicted_Class': [reverse_mapping[c] for c in y_pred],
    'Correct': y_pred == y_true
})

# Add probabilities
prob_cols = [f'Prob_{reverse_mapping[i]}' for i in range(len(reverse_mapping))]
prob_df = pd.DataFrame(y_prob, columns=prob_cols, index=results_df.index)
results_df = pd.concat([results_df, prob_df], axis=1)

results_df.to_csv('demo/classification_results.csv', index=False)
print('      Saved to: demo/classification_results.csv')
print()

print('=' * 80)
print('CLASSIFICATION COMPLETE')
print('=' * 80)
print()
print(f'Samples Classified: {len(y_pred)}')
print(f'Overall Accuracy:   {accuracy:.2%}')
print(f'Correct:            {(y_pred == y_true).sum()}')
print(f'Incorrect:          {(y_pred != y_true).sum()}')
print()

# Show sample predictions
print('SAMPLE PREDICTIONS (First 10):')
print('-' * 80)
print(f'{'True Class':<20} {'Predicted':<20} {'Result':<10} {'Confidence':<12}')
print('-' * 80)
for i in range(min(10, len(y_pred))):
    true_cls = reverse_mapping[y_true[i]]
    pred_cls = reverse_mapping[y_pred[i]]
    correct = 'CORRECT' if y_pred[i] == y_true[i] else 'WRONG'
    confidence = y_prob[i][y_pred[i]]
    print(f'{true_cls:<20} {pred_cls:<20} {correct:<10} {confidence:>6.1%}')
print()

# Per-class results
print('PER-CLASS ACCURACY:')
print('-' * 80)
for cls_num in sorted(np.unique(y_true)):
    cls_name = reverse_mapping[cls_num]
    mask = y_true == cls_num
    cls_correct = (y_pred[mask] == y_true[mask]).sum()
    cls_total = mask.sum()
    cls_acc = cls_correct / cls_total if cls_total > 0 else 0
    print(f'  {cls_name:<20} {cls_correct:>3}/{cls_total:<3} ({cls_acc:>6.1%})')
print()

# Confusion matrix data
print('CONFUSION MATRIX DATA:')
print('-' * 80)
from collections import defaultdict
confusion = defaultdict(lambda: defaultdict(int))
for t, p in zip(y_true, y_pred):
    confusion[reverse_mapping[t]][reverse_mapping[p]] += 1

print(f"{'True \\ Predicted':<20}", end='')
for cls in sorted(reverse_mapping.values()):
    print(f'{cls[:12]:>14}', end='')
print()
print('-' * 80)

for true_cls in sorted(reverse_mapping.values()):
    print(f'{true_cls:<20}', end='')
    for pred_cls in sorted(reverse_mapping.values()):
        count = confusion[true_cls][pred_cls]
        print(f'{count:>14}', end='')
    print()
print()

print('[OK] Classification complete!')
print()
"@

$pythonScript | Out-File -FilePath "demo\temp_classify.py" -Encoding UTF8

# Run classification
python demo\temp_classify.py

# Cleanup
Remove-Item "demo\temp_classify.py" -ErrorAction SilentlyContinue

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  Step 3 Complete - Classification finished" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""
Write-Host "Results saved to: demo\classification_results.csv" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next: Run 'powershell -File demo\step4_view_results.ps1'" -ForegroundColor Yellow
Write-Host ""
