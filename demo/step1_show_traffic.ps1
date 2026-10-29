# FlowSentry Demo - Step 1: Show Traffic Data
# Demonstrates NS2 traffic generation and conversion

$ErrorActionPreference = "Stop"
Set-Location D:\Sentry_Flow

Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  STEP 1: NETWORK TRAFFIC DATA" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

# Check if NS2 files exist
if (Test-Path "flowsentry.tcl") {
    Write-Host "[OK] NS2 Simulation Script Found" -ForegroundColor Green
    Write-Host "  File: flowsentry.tcl" -ForegroundColor Gray
    
    # Show snippet of TCL script
    Write-Host "`nNS2 Simulation Configuration:" -ForegroundColor Yellow
    Get-Content "flowsentry.tcl" | Select-Object -First 15
    Write-Host "  ..." -ForegroundColor Gray
    Write-Host ""
}

# Check for converted trace files
Write-Host "Checking for traffic capture files..." -ForegroundColor Yellow

$traceFiles = Get-ChildItem -Path "." -Filter "*.tr" -ErrorAction SilentlyContinue
if ($traceFiles) {
    Write-Host "[OK] Found $($traceFiles.Count) NS2 trace file(s)" -ForegroundColor Green
    foreach ($file in $traceFiles) {
        $size = [math]::Round($file.Length / 1KB, 2)
        Write-Host "  - $($file.Name) ($size KB)" -ForegroundColor Gray
    }
} else {
    Write-Host "[INFO] No NS2 trace files found (expected if not yet generated)" -ForegroundColor Yellow
}
Write-Host ""

# Show test data that will be used
Write-Host "Production Test Data:" -ForegroundColor Yellow
Write-Host "  Source: ISCX-VPN2016 Dataset (Scenario B)" -ForegroundColor White
Write-Host "  Location: data\processed\test\test.csv" -ForegroundColor Gray

if (Test-Path "data\processed\test\test.csv") {
    $lineCount = (Get-Content "data\processed\test\test.csv" | Measure-Object -Line).Lines - 1
    Write-Host "  Total Flows: $lineCount" -ForegroundColor White
    
    Write-Host "`nSample Network Flows (first 5):" -ForegroundColor Yellow
    
    # Activate venv if needed
    if (-not $env:VIRTUAL_ENV) {
        .\.venv\Scripts\Activate.ps1
    }
    
    $script = @"
import pandas as pd

# Load data
df = pd.read_csv('data/processed/test/test.csv', index_col=0)

# Show first 5 flows with key features
sample = df.head(5)[['duration', 'total_fiat', 'total_biat', 
                     'flowPktsPerSecond', 'flowBytesPerSecond', 'target_class']]

print(sample.to_string())

# Show traffic type distribution
print('\n\nTraffic Type Distribution:')
print(df['target_class'].value_counts().to_string())
"@
    
    $script | python
    
    Write-Host "`n[OK] Test data loaded successfully!" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Test data not found!" -ForegroundColor Red
}

Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  Step 1 Complete - Traffic data verified" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Run 'powershell -File demo\step2_model_accuracy.ps1'" -ForegroundColor Yellow
Write-Host ""
