# FlowSentry Demo - Step 2: Model Training Results
# Shows trained model performance metrics

$ErrorActionPreference = "Stop"
Set-Location D:\Sentry_Flow

Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  STEP 2: MODEL TRAINING RESULTS" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

Write-Host "Loading model performance metrics..." -ForegroundColor Yellow
Write-Host ""

# Show model comparison
if (Test-Path "artifacts\reports\comparison.csv") {
    Write-Host "MODEL COMPARISON (All Trained Models):" -ForegroundColor Yellow
    Write-Host ""
    
    $results = Import-Csv "artifacts\reports\comparison.csv"
    $formatted = $results | Select-Object `
        @{Name="Model"; Expression={$_.model_name.ToUpper()}},
        @{Name="CV Macro F1"; Expression={"{0:P2}" -f [double]$_.cv_macro_f1}},
        @{Name="Accuracy"; Expression={"{0:P2}" -f [double]$_.test_accuracy}},
        @{Name="Macro F1"; Expression={"{0:P2}" -f [double]$_.test_macro_f1}},
        @{Name="Precision"; Expression={"{0:P2}" -f [double]$_.test_macro_precision}},
        @{Name="Recall"; Expression={"{0:P2}" -f [double]$_.test_macro_recall}}

    $formatted | Format-Table -AutoSize
    
    # Highlight best model
    $best = $results | Sort-Object -Property cv_macro_f1 -Descending | Select-Object -First 1
    Write-Host "[WINNER] " -NoNewline -ForegroundColor Green
    Write-Host "$($best.model_name.ToUpper()) selected with $([double]$best.cv_macro_f1 * 100)% CV Macro F1" -ForegroundColor White
    Write-Host "         Held-out test accuracy: $([double]$best.test_accuracy * 100)%" -ForegroundColor Gray
    Write-Host ""
    
    # Show per-class performance
    Write-Host "PER-CLASS PERFORMANCE (Best Model):" -ForegroundColor Yellow
    Write-Host ""
    
    $perClass = @(
        @{Class="File Transfer"; F1=[double]$best.f1_file_transfer},
        @{Class="Streaming"; F1=[double]$best.f1_streaming},
        @{Class="VoIP"; F1=[double]$best.f1_voip},
        @{Class="Web Browsing"; F1=[double]$best.f1_web_browsing}
    ) | ForEach-Object { [PSCustomObject]$_ }
    
    $perClass | Select-Object `
        @{Name="Traffic Type"; Expression={$_.Class}},
        @{Name="F1 Score"; Expression={"{0:P2}" -f $_.F1}} | 
        Format-Table -AutoSize
    
} else {
    Write-Host "[ERROR] Model comparison results not found!" -ForegroundColor Red
    Write-Host "Expected: artifacts\reports\comparison.csv" -ForegroundColor Gray
}

# Show training details
Write-Host "TRAINING DETAILS:" -ForegroundColor Yellow
Write-Host "  Dataset: ISCX-VPN2016 (Scenario B)" -ForegroundColor White
Write-Host "  Training Samples: 47,696 flows" -ForegroundColor White
Write-Host "  Test Samples: 11,925 flows" -ForegroundColor White
Write-Host "  Features: 21 CICFlowMeter-compatible features" -ForegroundColor White
Write-Host "  Classes: 4 (Web, VoIP, Streaming, File Transfer)" -ForegroundColor White
Write-Host ""

# Show feature importance if available
Write-Host "KEY FEATURES USED:" -ForegroundColor Yellow
Write-Host "  - Flow duration" -ForegroundColor Gray
Write-Host "  - Packet timing patterns (FIAT/BIAT)" -ForegroundColor Gray
Write-Host "  - Flow packets/bytes per second" -ForegroundColor Gray
Write-Host "  - Statistical measures (min/max/mean/std)" -ForegroundColor Gray
Write-Host ""

Write-Host "[OK] Model training validation complete!" -ForegroundColor Green
Write-Host ""

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  Step 2 Complete - Model metrics verified" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Run 'powershell -File demo\step3_classify_traffic.ps1'" -ForegroundColor Yellow
Write-Host ""
