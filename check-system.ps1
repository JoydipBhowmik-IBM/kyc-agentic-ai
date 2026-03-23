#!/usr/bin/env powershell
# Pre-Deployment Checklist & Setup Verification

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  KYC Agentic AI - Pre-Deployment Verification Checklist       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

$checks = @{
    "Docker Installed" = {docker --version 2>$null}
    "Docker Running" = {docker ps 2>$null}
    "Docker Compose Available" = {docker-compose --version 2>$null}
    "Port 3000 Available" = {-not (netstat -ano 2>$null | findstr ":3000 ")}
    "Port 8000 Available" = {-not (netstat -ano 2>$null | findstr ":8000 ")}
    "Port 8001 Available" = {-not (netstat -ano 2>$null | findstr ":8001 ")}
    "Disk Space (2GB+)" = {(Get-Volume).SizeRemaining[0] -gt 2GB}
}

$passed = 0
$failed = 0

foreach ($check in $checks.GetEnumerator()) {
    Write-Host "Checking: $($check.Key)... " -NoNewline -ForegroundColor Yellow

    try {
        $result = & $check.Value
        if ($result) {
            Write-Host "✅ PASS" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "❌ FAIL" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host "❌ FAIL" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n"
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  RESULTS: $passed Passed | $failed Failed" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

if ($failed -eq 0) {
    Write-Host "✅ All checks passed! Ready to deploy." -ForegroundColor Green
    Write-Host "`nNext step: Double-click deploy.bat`n" -ForegroundColor Cyan
} else {
    Write-Host "❌ Some checks failed. Please fix before deploying." -ForegroundColor Red
    Write-Host "`nCommon solutions:" -ForegroundColor Yellow
    Write-Host "1. Start Docker Desktop from Windows Start Menu" -ForegroundColor Gray
    Write-Host "2. Close other applications using ports 3000, 8000-8005, 8010" -ForegroundColor Gray
    Write-Host "3. Ensure at least 2GB free disk space" -ForegroundColor Gray
    Write-Host "`n"
}

pause

