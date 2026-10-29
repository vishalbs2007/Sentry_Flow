# FlowSentry - Complete End-to-End Demonstration
# This shows the ENTIRE pipeline working: Data → Features → Classification → Results

param(
    [switch]$SkipIntro
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param($Title)
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param($Number, $Text)
    Write-Host "`n[$Number] " -NoNewline -ForegroundColor Yellow
    Write-Host $Text -ForegroundColor White
    Write-Host ("-" * 80) -ForegroundColor Gray
}

function Pause-Demo {
    param($Message = "Press Enter to continue...")
    Write-Host "`n$Message" -ForegroundColor Yellow
    $null = Read-Host
}

# Navigate to project
Set-Location D:\Sentry_Flow

# Activate venv
if (-not $env:VIRTUAL_ENV) {
    .\.venv\Scripts\Activate.ps1
}

if (-not $SkipIntro) {
    Clear-Host
    Write-Section "FLOWSENTRY - COMPLETE DEMONSTRATION"
    
    Write-Host "This demo shows the complete ML pipeline:" -ForegroundColor White
    Write-Host "  1. Model Training Results (98.12% accuracy)" -ForegroundColor Cyan
    Write-Host "  2. Test Data Loading" -ForegroundColor Cyan
    Write-Host "  3. Real Classification" -ForegroundColor Cyan
    Write-Host "  4. Results & Metrics" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Duration: ~3 minutes" -ForegroundColor Gray
    Write-Host ""
    
    Pause-Demo "Press Enter to start the demo..."
    Clear-Host
}

# ============================================================================
# PART 1: SHOW TRAINED MODEL
# ============================================================================

Write-Section "PART 1: TRAINED MODEL RESULTS"

Write-Step "1.1" "Loading Model Performance Metrics..."

# Show model comparison
Write-Host "`nMODEL COMPARISON:" -ForegroundColor Yellow
$results = Import-Csv "artifacts\reports\comparison.csv"
$formatted = $results | Select-Object `
    @{Name="Model"; Expression={$_.model_name.ToUpper()}},
    @{Name="Accuracy"; Expression={"{0:P2}" -f [double]$_.test_accuracy}},
    @{Name="Macro F1"; Expression={"{0:P2}" -f [double]$_.test_macro_f1}},
    @{Name="VoIP F1"; Expression={"{0:P2}" -f [double]$_.f1_voip}},
    @{Name="Web F1"; Expression={"{0:P2}" -f [double]$_.f1_web_browsing}}

$formatted | Format-Table -AutoSize

Write-Host "KEY FINDING: XGBoost selected with 98.12% accuracy" -ForegroundColor Green

Pause-Demo

# ============================================================================
# PART 2: LOAD TEST DATA
# ============================================================================

Write-Section "PART 2: LOADING TEST DATA"

Write-Step "2.1" "Loading pre-processed test flows..."

$testData = Import-Csv "data\processed\test\test.csv" | Select-Object -First 20

Write-Host "Test Data Sample (first 20 flows):" -ForegroundColor Yellow
Write-Host "  Total test flows: $(((Get-Content 'data\processed\test\test.csv' | Measure-Object -Line).Lines - 1))" -ForegroundColor White
Write-Host "  Showing first 20 flows..." -ForegroundColor White
Write-Host ""

# Show sample with key columns
$testData | Select-Object -First 5 `
    @{Name="Flow ID"; Expression={$_.PSObject.Properties.Name[0]}},
    duration,
    total_fiat,
    total_biat,
    @{Name="True Class"; Expression={$_.target_class}} | Format-Table -AutoSize

Write-Host "Features: duration, timing patterns, packet statistics (79 total)" -ForegroundColor Gray

Pause-Demo

# ============================================================================
# PART 3: RUN CLASSIFICATION
# ============================================================================

Write-Section "PART 3: REAL-TIME CLASSIFICATION"

Write-Step "3.1" "Loading trained model from registry..."

Write-Host "Model: Decision Tree (Active)" -ForegroundColor Cyan
Write-Host "Features: 9 selected from 79 extracted" -ForegroundColor Gray
Write-Host "Registry: artifacts\registry\decision_tree_20261014_011743\" -ForegroundColor Gray

Write-Host "`n[Loading model...]" -ForegroundColor Yellow

# Create a simple Python script to do actual classification
$pythonScript = @"
import pandas as pd
import joblib
import sys
import numpy as np

# Load test data
print('Loading test data...')
test_data = pd.read_csv('data/processed/test/test.csv', index_col=0)

# Take sample
sample_size = 100
test_sample = test_data.sample(n=min(sample_size, len(test_data)), random_state=42)

# Load model
print('Loading trained model...')
pipeline = joblib.load('artifacts/registry/decision_tree_20261014_011743/pipeline.joblib')

# Get the exact features the model expects
expected_features = pipeline.feature_names_in_
print(f'Model expects {len(expected_features)} features')

# Define class mapping (alphabetical order matches model.classes_ = [0,1,2,3])
class_mapping = {
    'File Transfer': 0,
    'Streaming': 1,
    'VoIP': 2,
    'Web Browsing': 3
}
reverse_mapping = {v: k for k, v in class_mapping.items()}

# Encode true labels to match model's numeric encoding
y_true_str = test_sample['target_class']
y_true = np.array([class_mapping[cls] for cls in y_true_str])

# Make sure we have those columns
X_test = test_sample[expected_features]

# Predict
print('Classifying flows...')
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)

# Calculate accuracy
accuracy = (y_pred == y_true).mean()

# Save results (decode back to string class names)
results_df = pd.DataFrame({
    'True_Class': [reverse_mapping[c] for c in y_true],
    'Predicted_Class': [reverse_mapping[c] for c in y_pred],
    'Correct': y_pred == y_true
})

# Add probabilities with class names
prob_cols = [f'Prob_{reverse_mapping[i]}' for i in range(len(reverse_mapping))]
prob_df = pd.DataFrame(y_prob, columns=prob_cols, index=results_df.index)
results_df = pd.concat([results_df, prob_df], axis=1)

results_df.to_csv('artifacts/demo_results.csv', index=False)

# Print summary
print(f'\n=== CLASSIFICATION COMPLETE ===')
print(f'Samples Classified: {len(y_pred)}')
print(f'Accuracy: {accuracy:.2%}')
print(f'Correct: {(y_pred == y_true).sum()}')
print(f'Incorrect: {(y_pred != y_true).sum()}')

# Per-class accuracy
print('\nPer-Class Results:')
for cls_num in sorted(np.unique(y_true)):
    cls_name = reverse_mapping[cls_num]
    mask = y_true == cls_num
    cls_acc = (y_pred[mask] == y_true[mask]).mean()
    cls_count = mask.sum()
    print(f'  {cls_name}: {cls_acc:.1%} ({cls_count} samples)')
"@

$pythonScript | Out-File -FilePath "temp_classify.py" -Encoding UTF8

Write-Host "`n[Classifying 100 test samples...]" -ForegroundColor Yellow
python temp_classify.py

Write-Host "`n[Classification complete!]" -ForegroundColor Green

Pause-Demo

# ============================================================================
# PART 4: SHOW RESULTS
# ============================================================================

Write-Section "PART 4: CLASSIFICATION RESULTS"

Write-Step "4.1" "Analyzing predictions..."

# Load results
$results = Import-Csv "artifacts\demo_results.csv"

Write-Host "`nSample Predictions:" -ForegroundColor Yellow
$results | Select-Object -First 10 `
    True_Class,
    Predicted_Class,
    @{Name="Match"; Expression={if ($_.Correct -eq "True") {"OK"} else {"X"}}},
    @{Name="Confidence"; Expression={
        $probs = @($_.Prob_File_Transfer, $_.Prob_Streaming, $_.Prob_VoIP, $_.Prob_Web_Browsing)
        $maxProb = ($probs | Measure-Object -Maximum).Maximum
        "{0:P1}" -f [double]$maxProb
    }} | Format-Table -AutoSize

Write-Host "`nOVERALL ACCURACY:" -ForegroundColor Yellow
$correct = ($results | Where-Object {$_.Correct -eq "True"}).Count
$total = $results.Count
$accuracy = $correct / $total
Write-Host "  Correct:   $correct / $total" -ForegroundColor Green
Write-Host "  Accuracy:  $($accuracy.ToString('P2'))" -ForegroundColor Green

Write-Host "`nPER-CLASS BREAKDOWN:" -ForegroundColor Yellow
$results | Group-Object True_Class | ForEach-Object {
    $class = $_.Name
    $classResults = $_.Group
    $classCorrect = ($classResults | Where-Object {$_.Correct -eq "True"}).Count
    $classTotal = $classResults.Count
    $classAcc = $classCorrect / $classTotal
    Write-Host ("  {0,-20} {1}/{2} ({3:P1})" -f $class, $classCorrect, $classTotal, $classAcc) -ForegroundColor Cyan
}

Pause-Demo

# ============================================================================
# PART 5: CONFUSION MATRIX
# ============================================================================

Write-Section "PART 5: DETAILED ANALYSIS"

Write-Step "5.1" "Generating confusion matrix..."

# Count predictions
$matrix = @{}
$classes = $results.True_Class | Sort-Object -Unique

foreach ($trueClass in $classes) {
    $matrix[$trueClass] = @{}
    foreach ($predClass in $classes) {
        $count = ($results | Where-Object {
            $_.True_Class -eq $trueClass -and $_.Predicted_Class -eq $predClass
        }).Count
        $matrix[$trueClass][$predClass] = $count
    }
}

Write-Host "`nCONFUSION MATRIX:" -ForegroundColor Yellow
Write-Host "Rows = True Class, Columns = Predicted Class" -ForegroundColor Gray
Write-Host ""

# Header
Write-Host ("{0,-20}" -f "True \ Predicted") -NoNewline -ForegroundColor Yellow
foreach ($cls in $classes) {
    Write-Host ("{0,15}" -f $cls.Substring(0, [Math]::Min(12, $cls.Length))) -NoNewline -ForegroundColor Yellow
}
Write-Host ""
Write-Host ("-" * 80) -ForegroundColor Gray

# Rows
foreach ($trueClass in $classes) {
    Write-Host ("{0,-20}" -f $trueClass.Substring(0, [Math]::Min(18, $trueClass.Length))) -NoNewline -ForegroundColor White
    foreach ($predClass in $classes) {
        $count = $matrix[$trueClass][$predClass]
        if ($trueClass -eq $predClass) {
            Write-Host ("{0,15}" -f $count) -NoNewline -ForegroundColor Green
        } else {
            Write-Host ("{0,15}" -f $count) -NoNewline -ForegroundColor Red
        }
    }
    Write-Host ""
}

Pause-Demo

# ============================================================================
# PART 6: SUMMARY
# ============================================================================

Write-Section "DEMONSTRATION SUMMARY"

Write-Host "WHAT WE JUST DEMONSTRATED:" -ForegroundColor Yellow
Write-Host "  [OK] Loaded trained model (98.12% on full test set)" -ForegroundColor Green
Write-Host "  [OK] Classified 100 real network flows" -ForegroundColor Green
Write-Host "  [OK] Achieved $($accuracy.ToString('P2')) accuracy on sample" -ForegroundColor Green
Write-Host "  [OK] Showed per-class performance" -ForegroundColor Green
Write-Host "  [OK] Generated confusion matrix" -ForegroundColor Green

Write-Host "`nKEY METRICS:" -ForegroundColor Yellow
Write-Host "  Training Data:   47,696 flows" -ForegroundColor White
Write-Host "  Test Data:       11,925 flows" -ForegroundColor White
Write-Host "  Test Accuracy:   98.12% (XGBoost)" -ForegroundColor White
Write-Host "  Demo Accuracy:   $($accuracy.ToString('P2')) (Decision Tree on 100 samples)" -ForegroundColor White
Write-Host "  Classes:         4 (Web, VoIP, Streaming, FTP)" -ForegroundColor White
Write-Host "  Features:        9 selected from 79 extracted" -ForegroundColor White

Write-Host "`nFILES GENERATED:" -ForegroundColor Yellow
Write-Host "  artifacts\demo_results.csv - Detailed predictions" -ForegroundColor Gray

Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  DEMONSTRATION COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

# Cleanup
Remove-Item "temp_classify.py" -ErrorAction SilentlyContinue

Write-Host "Demo artifacts saved. You can review:" -ForegroundColor Yellow
Write-Host "  type artifacts\demo_results.csv" -ForegroundColor Gray
Write-Host ""
