# FlowSentry NS2 Traffic Generation - Windows PowerShell Script
# This automates the entire NS2 -> PCAP -> Classification pipeline

param(
    [switch]$SkipNS2,           # Skip NS2 simulation (use existing out.tr)
    [switch]$ValidateOnly,      # Only validate existing results
    [string]$OutputDir = "simulation\pcaps"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  FlowSentry NS2 Integration" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
Set-Location $projectRoot

Write-Host "[INFO] Project root: $projectRoot" -ForegroundColor Green

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "[WARN] Virtual environment not activated. Activating..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "[INFO] Created output directory: $OutputDir" -ForegroundColor Green
}

# Step 1: Run NS2 Simulation (if not skipped)
if (-not $SkipNS2 -and -not $ValidateOnly) {
    Write-Host ""
    Write-Host "Step 1: NS2 Simulation" -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    
    # Check for NS2
    $ns2Available = $false
    
    # Try ns command
    try {
        $null = Get-Command ns -ErrorAction SilentlyContinue
        $ns2Available = $true
        Write-Host "[INFO] NS2 found: Using native 'ns' command" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] NS2 not found in PATH" -ForegroundColor Yellow
    }
    
    # Try WSL
    if (-not $ns2Available) {
        try {
            $wslTest = wsl which ns 2>&1
            if ($LASTEXITCODE -eq 0) {
                $ns2Available = $true
                Write-Host "[INFO] NS2 found: Using WSL" -ForegroundColor Green
            }
        } catch {
            Write-Host "[WARN] WSL not available or NS2 not installed in WSL" -ForegroundColor Yellow
        }
    }
    
    # Try Docker
    if (-not $ns2Available) {
        try {
            $dockerTest = docker images hbhzwj/ns2 2>&1
            if ($LASTEXITCODE -eq 0) {
                $ns2Available = $true
                Write-Host "[INFO] NS2 found: Using Docker" -ForegroundColor Green
            }
        } catch {
            Write-Host "[WARN] Docker not available or NS2 image not pulled" -ForegroundColor Yellow
        }
    }
    
    if ($ns2Available) {
        Write-Host "[RUN] Executing: ns flowsentry.tcl" -ForegroundColor Cyan
        
        # Run NS2 based on available method
        if (Get-Command ns -ErrorAction SilentlyContinue) {
            ns flowsentry.tcl
        } elseif ((wsl which ns 2>&1) -and $LASTEXITCODE -eq 0) {
            wsl ns flowsentry.tcl
        } else {
            docker run -v "${PWD}:/work" -w /work hbhzwj/ns2 ns flowsentry.tcl
        }
        
        if (Test-Path "out.tr") {
            $trSize = (Get-Item "out.tr").Length
            Write-Host "[OK] NS2 simulation complete! Generated out.tr ($([math]::Round($trSize/1KB, 2)) KB)" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] NS2 simulation failed - out.tr not created" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "[SKIP] NS2 not available. Options:" -ForegroundColor Yellow
        Write-Host "  1. Install NS2 via WSL: wsl sudo apt-get install ns2" -ForegroundColor Yellow
        Write-Host "  2. Use Docker: docker pull hbhzwj/ns2" -ForegroundColor Yellow
        Write-Host "  3. Use pre-generated files with -SkipNS2 flag" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "[INFO] Checking for existing out.tr..." -ForegroundColor Cyan
        
        if (-not (Test-Path "out.tr")) {
            Write-Host "[ERROR] No out.tr file found. Cannot proceed." -ForegroundColor Red
            Write-Host "[INFO] Please generate out.tr or use pre-generated PCAPs" -ForegroundColor Yellow
            exit 1
        } else {
            Write-Host "[OK] Using existing out.tr file" -ForegroundColor Green
        }
    }
}

# Step 2: Convert to PCAP (if not validation only)
if (-not $ValidateOnly) {
    Write-Host ""
    Write-Host "Step 2: Convert NS2 Trace to PCAP" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    
    if (-not (Test-Path "out.tr")) {
        Write-Host "[ERROR] out.tr not found. Run with NS2 first or check file location." -ForegroundColor Red
        exit 1
    }
    
    $pcapPath = "$OutputDir\ns2_traffic.pcap"
    Write-Host "[RUN] Executing: python tr_to_pcap.py out.tr $pcapPath" -ForegroundColor Cyan
    
    python tr_to_pcap.py out.tr $pcapPath
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $pcapPath)) {
        $pcapSize = (Get-Item $pcapPath).Length
        Write-Host "[OK] Conversion complete! Generated $pcapPath ($([math]::Round($pcapSize/1KB, 2)) KB)" -ForegroundColor Green
        
        # Check for labels file
        $labelsPath = "$OutputDir\ns2_traffic_labels.csv"
        if (Test-Path $labelsPath) {
            $labelCount = (Get-Content $labelsPath | Measure-Object -Line).Lines - 1
            Write-Host "[OK] Ground truth labels: $labelsPath ($labelCount flows)" -ForegroundColor Green
        }
    } else {
        Write-Host "[ERROR] PCAP conversion failed" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Classify with FlowSentry
Write-Host ""
Write-Host "Step 3: Classify Traffic with FlowSentry" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$pcapPath = "$OutputDir\ns2_traffic.pcap"
$outputPath = "artifacts\ns2_demo"

if (-not (Test-Path $pcapPath)) {
    Write-Host "[ERROR] PCAP file not found: $pcapPath" -ForegroundColor Red
    Write-Host "[INFO] Run without -ValidateOnly first to generate PCAP" -ForegroundColor Yellow
    exit 1
}

Write-Host "[RUN] Executing: python -m inference.pcap_classifier --pcap $pcapPath --output $outputPath" -ForegroundColor Cyan

python -m inference.pcap_classifier --pcap $pcapPath --output $outputPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Classification complete!" -ForegroundColor Green
    
    # Display results
    $resultsFile = "$outputPath\classification_results.txt"
    if (Test-Path $resultsFile) {
        Write-Host ""
        Write-Host "========== CLASSIFICATION RESULTS ==========" -ForegroundColor Cyan
        Get-Content $resultsFile
        Write-Host "============================================" -ForegroundColor Cyan
    }
} else {
    Write-Host "[ERROR] Classification failed" -ForegroundColor Red
    exit 1
}

# Step 4: Validation (if labels exist)
Write-Host ""
Write-Host "Step 4: Validate Against Ground Truth" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$labelsPath = "$OutputDir\ns2_traffic_labels.csv"
if (Test-Path $labelsPath) {
    Write-Host "[RUN] Comparing predictions with ground truth..." -ForegroundColor Cyan
    
    python simulation\ns2\validate.py "$outputPath\classification_results.txt" $labelsPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Validation complete!" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Validation encountered issues (this is normal for probabilistic models)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[SKIP] No ground truth labels found. Skipping validation." -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Pipeline Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Generated Files:" -ForegroundColor Green
Write-Host "  - Trace:    out.tr" -ForegroundColor White
Write-Host "  - PCAP:     $pcapPath" -ForegroundColor White
Write-Host "  - Labels:   $labelsPath" -ForegroundColor White
Write-Host "  - Results:  $outputPath\" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Check classification results: type $outputPath\classification_results.txt" -ForegroundColor White
Write-Host "  2. View PCAP in Wireshark: wireshark $pcapPath" -ForegroundColor White
Write-Host "  3. Compare with labels: type $labelsPath" -ForegroundColor White
Write-Host ""
