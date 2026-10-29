# FlowSentry Demo - Step 4: View Detailed Results
# Shows comprehensive analysis of classification results

$ErrorActionPreference = "Stop"
Set-Location D:\Sentry_Flow

Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  STEP 4: DETAILED RESULTS ANALYSIS" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "demo\classification_results.csv")) {
    Write-Host "[ERROR] Classification results not found!" -ForegroundColor Red
    Write-Host "Please run Step 3 first: powershell -File demo\step3_classify_traffic.ps1" -ForegroundColor Yellow
    exit 1
}

# Load results
Write-Host "Loading classification results..." -ForegroundColor Yellow
$results = Import-Csv "demo\classification_results.csv"
Write-Host "[OK] Loaded $($results.Count) predictions" -ForegroundColor Green
Write-Host ""

# Overall statistics
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host "  OVERALL PERFORMANCE" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host ""

$correct = ($results | Where-Object {$_.Correct -eq "True"}).Count
$incorrect = $results.Count - $correct
$accuracy = $correct / $results.Count

Write-Host "Total Samples:     $($results.Count)" -ForegroundColor White
Write-Host "Correct:           $correct " -NoNewline -ForegroundColor Green
Write-Host "($([math]::Round($accuracy * 100, 2))%)" -ForegroundColor Green
Write-Host "Incorrect:         $incorrect " -NoNewline -ForegroundColor Red
Write-Host "($([math]::Round((1 - $accuracy) * 100, 2))%)" -ForegroundColor Red
Write-Host ""

# Per-class breakdown
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host "  PER-CLASS BREAKDOWN" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host ""

$results | Group-Object True_Class | Sort-Object Name | ForEach-Object {
    $class = $_.Name
    $classResults = $_.Group
    $classCorrect = ($classResults | Where-Object {$_.Correct -eq "True"}).Count
    $classTotal = $classResults.Count
    $classAcc = $classCorrect / $classTotal
    
    Write-Host ("{0,-20}" -f $class) -NoNewline -ForegroundColor Cyan
    Write-Host " {0,3}/{1,-3} " -f $classCorrect, $classTotal -NoNewline
    if ($classAcc -ge 0.95) {
        Write-Host "({0:P1}) [EXCELLENT]" -f $classAcc -ForegroundColor Green
    } elseif ($classAcc -ge 0.85) {
        Write-Host "({0:P1}) [GOOD]" -f $classAcc -ForegroundColor Yellow
    } else {
        Write-Host "({0:P1}) [NEEDS REVIEW]" -f $classAcc -ForegroundColor Red
    }
}
Write-Host ""

# Sample predictions table
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host "  SAMPLE PREDICTIONS (First 15)" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host ""

$results | Select-Object -First 15 `
    @{Name="True Class"; Expression={$_.True_Class}},
    @{Name="Predicted"; Expression={$_.Predicted_Class}},
    @{Name="Result"; Expression={if ($_.Correct -eq "True") {"OK"} else {"WRONG"}}},
    @{Name="Confidence"; Expression={
        $probs = @(
            [double]$_.'Prob_File Transfer',
            [double]$_.'Prob_Streaming',
            [double]$_.'Prob_VoIP',
            [double]$_.'Prob_Web Browsing'
        )
        $maxProb = ($probs | Measure-Object -Maximum).Maximum
        "{0:P1}" -f $maxProb
    }} | Format-Table -AutoSize

# Confusion matrix
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host "  CONFUSION MATRIX" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Yellow
Write-Host ""
Write-Host "Rows = True Class, Columns = Predicted Class" -ForegroundColor Gray
Write-Host ""

$classes = $results.True_Class | Sort-Object -Unique
$matrix = @{}

foreach ($trueClass in $classes) {
    $matrix[$trueClass] = @{}
    foreach ($predClass in $classes) {
        $count = ($results | Where-Object {
            $_.True_Class -eq $trueClass -and $_.Predicted_Class -eq $predClass
        }).Count
        $matrix[$trueClass][$predClass] = $count
    }
}

# Header
Write-Host ("{0,-20}" -f "True \ Predicted") -NoNewline -ForegroundColor Yellow
foreach ($cls in $classes) {
    $shortName = $cls.Substring(0, [Math]::Min(12, $cls.Length))
    Write-Host ("{0,14}" -f $shortName) -NoNewline -ForegroundColor Yellow
}
Write-Host ""
Write-Host ("-" * 80) -ForegroundColor Gray

# Rows
foreach ($trueClass in $classes) {
    $shortName = $trueClass.Substring(0, [Math]::Min(18, $trueClass.Length))
    Write-Host ("{0,-20}" -f $shortName) -NoNewline -ForegroundColor White
    foreach ($predClass in $classes) {
        $count = $matrix[$trueClass][$predClass]
        if ($trueClass -eq $predClass) {
            Write-Host ("{0,14}" -f $count) -NoNewline -ForegroundColor Green
        } else {
            if ($count -gt 0) {
                Write-Host ("{0,14}" -f $count) -NoNewline -ForegroundColor Red
            } else {
                Write-Host ("{0,14}" -f $count) -NoNewline -ForegroundColor Gray
            }
        }
    }
    Write-Host ""
}
Write-Host ""

# Misclassified examples
$misclassified = $results | Where-Object {$_.Correct -eq "False"}
if ($misclassified.Count -gt 0) {
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host "  MISCLASSIFIED EXAMPLES" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Total misclassifications: $($misclassified.Count)" -ForegroundColor Red
    Write-Host ""
    
    $misclassified | Select-Object -First 5 `
        @{Name="True Class"; Expression={$_.True_Class}},
        @{Name="Predicted As"; Expression={$_.Predicted_Class}},
        @{Name="Confidence"; Expression={
            $probs = @(
                [double]$_.'Prob_File Transfer',
                [double]$_.'Prob_Streaming',
                [double]$_.'Prob_VoIP',
                [double]$_.'Prob_Web Browsing'
            )
            $maxProb = ($probs | Measure-Object -Maximum).Maximum
            "{0:P1}" -f $maxProb
        }} | Format-Table -AutoSize
    
    Write-Host "Note: These edge cases show where the model needs improvement" -ForegroundColor Gray
    Write-Host ""
}

# Summary
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "  ANALYSIS COMPLETE" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""
Write-Host "Key Findings:" -ForegroundColor Yellow
Write-Host "  [*] Overall accuracy: $($accuracy.ToString('P2'))" -ForegroundColor White
Write-Host "  [*] Best performing: " -NoNewline -ForegroundColor White
$bestClass = ($results | Group-Object True_Class | ForEach-Object {
    [PSCustomObject]@{
        Class = $_.Name
        Accuracy = (($_.Group | Where-Object {$_.Correct -eq "True"}).Count / $_.Group.Count)
    }
} | Sort-Object -Property Accuracy -Descending | Select-Object -First 1)
Write-Host "$($bestClass.Class) ($($bestClass.Accuracy.ToString('P1')))" -ForegroundColor Green

Write-Host "  [*] Results saved: demo\classification_results.csv" -ForegroundColor White
Write-Host ""
Write-Host "[OK] All demo steps completed successfully!" -ForegroundColor Green
Write-Host ""
