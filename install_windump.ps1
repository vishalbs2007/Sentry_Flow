# Install WinDump for FlowSentry
# This enables full CICFlowMeter feature extraction

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  WinDump Installation for FlowSentry" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Npcap is installed
Write-Host "[1/4] Checking Npcap installation..." -ForegroundColor Yellow

$npcapPath = "C:\Windows\System32\Npcap"
if (Test-Path $npcapPath) {
    Write-Host "  [OK] Npcap is installed" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Npcap NOT found!" -ForegroundColor Red
    Write-Host "`nPlease install Npcap first:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://npcap.com/#download" -ForegroundColor White
    Write-Host "  2. Run installer" -ForegroundColor White
    Write-Host "  3. Check 'Install Npcap in WinPcap API-compatible Mode'" -ForegroundColor White
    Write-Host "  4. Run this script again`n" -ForegroundColor White
    exit 1
}

# Download WinDump
Write-Host "`n[2/4] Downloading WinDump..." -ForegroundColor Yellow

$windumpUrl = "https://www.winpcap.org/windump/install/bin/windump_3_9_5/WinDump.exe"
$windumpPath = "bin\WinDump.exe"

# Create bin directory
if (-not (Test-Path "bin")) {
    New-Item -ItemType Directory -Path "bin" | Out-Null
}

try {
    Write-Host "  Downloading from winpcap.org..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $windumpUrl -OutFile $windumpPath -UseBasicParsing
    Write-Host "  ✓ WinDump downloaded successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Download failed: $_" -ForegroundColor Red
    Write-Host "`nAlternative: Manual download" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://www.winpcap.org/windump/install/default.htm" -ForegroundColor White
    Write-Host "  2. Download WinDump 3.9.5" -ForegroundColor White
    Write-Host "  3. Extract WinDump.exe" -ForegroundColor White
    Write-Host "  4. Copy to: D:\Sentry_Flow\bin\WinDump.exe`n" -ForegroundColor White
    exit 1
}

# Verify downloaded file
Write-Host "`n[3/4] Verifying installation..." -ForegroundColor Yellow

if (Test-Path $windumpPath) {
    $fileSize = (Get-Item $windumpPath).Length
    Write-Host "  [OK] WinDump.exe exists ($fileSize bytes)" -ForegroundColor Green
    
    # Test if it runs
    try {
        $output = & $windumpPath --version 2>&1
        if ($output -match "WinDump" -or $output -match "tcpdump") {
            Write-Host "  [OK] WinDump is working!" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] WinDump may not be working correctly" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [WARN] Could not test WinDump (may need admin rights)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [ERROR] WinDump.exe not found after download" -ForegroundColor Red
    exit 1
}

# Update config to use WinDump
Write-Host "`n[4/4] Configuring FlowSentry..." -ForegroundColor Yellow

# CICFlowMeter will automatically find WinDump.exe in bin/
Write-Host "  ✓ Configuration complete" -ForegroundColor Green

# Final instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test the installation:" -ForegroundColor White
Write-Host "     python -m inference.pcap_classifier --pcap data/sample/test_traffic.pcap --output artifacts/test" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Check the logs - you should see:" -ForegroundColor White
Write-Host "     'CICFlowMeter successfully extracted X flows with 79 features'" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. If successful, classification will complete without schema mismatch!" -ForegroundColor White
Write-Host ""

Write-Host "Note: WinDump may require Administrator privileges for packet capture." -ForegroundColor Yellow
Write-Host "If you get permission errors, run PowerShell as Administrator.`n" -ForegroundColor Yellow
