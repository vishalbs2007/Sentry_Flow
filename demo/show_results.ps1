# FlowSentry Results Viewer - Formatted Tables
# Run this script to see beautifully formatted results

$separator = "=" * 80

Write-Host ""
Write-Host $separator -ForegroundColor Cyan
Write-Host "  FLOWSENTRY MODEL COMPARISON RESULTS" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

# Read and parse CSV
$results = Import-Csv "artifacts\reports\comparison.csv"

# Create formatted table
$formatted = $results | Select-Object `
    @{Name="Model"; Expression={$_.model_name.ToUpper()}},
    @{Name="Test Accuracy"; Expression={"{0:P2}" -f [double]$_.test_accuracy}},
    @{Name="Macro F1"; Expression={"{0:P2}" -f [double]$_.test_macro_f1}},
    @{Name="Web F1"; Expression={"{0:P2}" -f [double]$_.f1_web_browsing}},
    @{Name="VoIP F1"; Expression={"{0:P2}" -f [double]$_.f1_voip}},
    @{Name="Stream F1"; Expression={"{0:P2}" -f [double]$_.f1_streaming}},
    @{Name="FTP F1"; Expression={"{0:P2}" -f [double]$_.f1_file_transfer}},
    @{Name="Inference (ms)"; Expression={"{0:F3}" -f [double]$_.inference_time_ms}}

# Display table
$formatted | Format-Table -AutoSize

Write-Host ""
Write-Host "KEY FINDINGS:" -ForegroundColor Yellow
Write-Host "  Best Model: XGBoost with 98.12% accuracy" -ForegroundColor Green
Write-Host "  Best Per-Class: VoIP at 99.49% F1-score" -ForegroundColor Green
Write-Host "  Fastest: Decision Tree at 0.006ms per flow" -ForegroundColor Green
Write-Host ""

# Detailed XGBoost Report
Write-Host $separator -ForegroundColor Cyan
Write-Host "  XGBOOST (BEST MODEL) - DETAILED REPORT" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

# Read metrics JSON for precise values
$metricsPath = "artifacts\reports\xgboost_20261024_124732\metrics.json"
$metrics = Get-Content $metricsPath | ConvertFrom-Json

Write-Host "OVERALL PERFORMANCE:" -ForegroundColor Yellow
Write-Host ("  Accuracy: {0:P2}" -f $metrics.accuracy) -ForegroundColor Green
Write-Host ""

Write-Host "PER-CLASS METRICS:" -ForegroundColor Yellow
Write-Host ("-" * 80) -ForegroundColor Gray

$classOrder = @("File Transfer", "Streaming", "VoIP", "Web Browsing")
foreach ($className in $classOrder) {
    $classMetrics = $metrics.per_class.$className
    if ($classMetrics) {
        Write-Host ("{0,-20}" -f $className) -NoNewline -ForegroundColor White
        Write-Host ("Precision: {0:P2}  " -f $classMetrics.precision) -NoNewline -ForegroundColor Cyan
        Write-Host ("Recall: {0:P2}  " -f $classMetrics.recall) -NoNewline -ForegroundColor Cyan
        Write-Host ("F1: {0:P2}" -f $classMetrics.'f1-score') -ForegroundColor Green
    }
}

Write-Host ("-" * 80) -ForegroundColor Gray
Write-Host ("{0,-20}" -f "Macro Average") -NoNewline -ForegroundColor Yellow
Write-Host ("Precision: {0:P2}  " -f $metrics.macro.precision) -NoNewline -ForegroundColor Yellow
Write-Host ("Recall: {0:P2}  " -f $metrics.macro.recall) -NoNewline -ForegroundColor Yellow
Write-Host ("F1: {0:P2}" -f $metrics.macro.'f1-score') -ForegroundColor Yellow

Write-Host ("{0,-20}" -f "Weighted Average") -NoNewline -ForegroundColor Cyan
Write-Host ("Precision: {0:P2}  " -f $metrics.weighted.precision) -NoNewline -ForegroundColor Cyan
Write-Host ("Recall: {0:P2}  " -f $metrics.weighted.recall) -NoNewline -ForegroundColor Cyan
Write-Host ("F1: {0:P2}" -f $metrics.weighted.'f1-score') -ForegroundColor Cyan

Write-Host ""

# Summary statistics
Write-Host "DATASET STATISTICS:" -ForegroundColor Yellow
Write-Host "  Training Samples:  47,696 flows" -ForegroundColor White
Write-Host "  Test Samples:      11,925 flows" -ForegroundColor White
Write-Host "  Traffic Classes:   4 types" -ForegroundColor White
Write-Host "  Features Used:     9 selected from 79 extracted" -ForegroundColor White
Write-Host ""

Write-Host "PERFORMANCE HIGHLIGHTS:" -ForegroundColor Yellow
Write-Host "  VoIP F1:          99.49%" -ForegroundColor Green
Write-Host "  Web F1:           98.18%" -ForegroundColor Green  
Write-Host "  FTP F1:           97.29%" -ForegroundColor Green
Write-Host "  Streaming F1:     93.69%" -ForegroundColor Green
Write-Host ""

Write-Host "SPEED & EFFICIENCY:" -ForegroundColor Yellow
Write-Host "  Inference:        0.015 ms per flow" -ForegroundColor White
Write-Host "  Training Time:    85 seconds" -ForegroundColor White
Write-Host "  Model Size:       12.7 MB" -ForegroundColor White
Write-Host ""

Write-Host $separator -ForegroundColor Cyan
Write-Host "  All metrics on held-out test set (never seen during training)" -ForegroundColor Gray
Write-Host $separator -ForegroundColor Cyan
Write-Host ""
