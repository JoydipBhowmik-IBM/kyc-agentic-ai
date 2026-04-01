@echo off
REM =====================================================================
REM KYC/AML Agentic AI - Complete Deployment Script
REM =====================================================================
setlocal enabledelayedexpansion
pushd "%~dp0"
set PROJECT_NAME=KYC-AML Agentic AI
set COMPOSE_FILE=docker-compose.yml
set LOG_FILE=deployment.log
set START_TIME=%time%
echo. > "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
echo Deployment Log - Started at %START_TIME% >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
:start
cls
echo =====================================================================
echo            KYC/AML Agentic AI - Deployment Script
echo                   Version 1.0 - April 1, 2026
echo =====================================================================
echo.
echo Project: %PROJECT_NAME%
echo Log File: %LOG_FILE%
echo.
echo [INFO] Deployment started at %START_TIME%
echo [INFO] Deployment started at %START_TIME% >> "%LOG_FILE%"
echo.
echo =====================================================================
echo STEP 1: Checking Prerequisites
echo =====================================================================
echo. >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
echo STEP 1: Checking Prerequisites >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
echo.
echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo [ERROR] Docker is not installed or not in PATH >> "%LOG_FILE%"
    goto error_exit
)
for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo [SUCCESS] Docker found: %DOCKER_VERSION%
echo [SUCCESS] Docker found: %DOCKER_VERSION% >> "%LOG_FILE%"
echo Checking Docker Compose installation...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed or not in PATH
    echo [ERROR] Docker Compose is not installed or not in PATH >> "%LOG_FILE%"
    goto error_exit
)
for /f "tokens=3" %%i in ('docker-compose --version') do set COMPOSE_VERSION=%%i
echo [SUCCESS] Docker Compose found: !COMPOSE_VERSION!
echo [SUCCESS] Docker Compose found: !COMPOSE_VERSION! >> "%LOG_FILE%"
echo Verifying docker-compose.yml exists...
if not exist %COMPOSE_FILE% (
    echo [ERROR] docker-compose.yml not found in %cd%
    echo [ERROR] docker-compose.yml not found in %cd% >> "%LOG_FILE%"
    goto error_exit
)
echo [SUCCESS] docker-compose.yml verified
echo [SUCCESS] docker-compose.yml verified >> "%LOG_FILE%"
echo.
echo =====================================================================
echo STEP 2: Docker Cleanup (Optional)
echo =====================================================================
echo. >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
echo STEP 2: Docker Cleanup (Optional) >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
echo.
echo Do you want to perform cleanup? (y/n)
set /p CLEANUP="Enter choice (y/n): "
if /i "%CLEANUP%"=="y" (
    echo [INFO] Starting Docker cleanup...
    echo [INFO] Starting Docker cleanup... >> "%LOG_FILE%"
    echo Removing stopped containers...
    docker container prune -f >>"%LOG_FILE%" 2>&1
    echo [SUCCESS] Stopped containers removed >> "%LOG_FILE%"
    echo Removing dangling images...
    docker image prune -f >>"%LOG_FILE%" 2>&1
    echo [SUCCESS] Dangling images removed >> "%LOG_FILE%"
    echo Removing unused volumes...
    docker volume prune -f >>"%LOG_FILE%" 2>&1
    echo [SUCCESS] Unused volumes removed >> "%LOG_FILE%"
) else (
    echo [INFO] Cleanup skipped >> "%LOG_FILE%"
)
echo.
echo =====================================================================
echo STEP 3: Building Docker Images
echo =====================================================================
echo. >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
echo STEP 3: Building Docker Images >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
docker-compose build >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] Docker build failed
    goto error_exit
)
echo [SUCCESS] All Docker images built successfully >> "%LOG_FILE%"
echo.
echo =====================================================================
echo STEP 4: Starting Containers with Live Log Monitoring
echo =====================================================================
echo. >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"
echo STEP 4: Starting Containers with Live Log Monitoring >> "%LOG_FILE%"
echo ===================================================================== >> "%LOG_FILE%"

echo [INFO] Starting all services with live log monitoring in current terminal...
echo [INFO] All service logs will be displayed here with service names prefixed.
echo [INFO] Press Ctrl+C to stop all services and exit.
echo.

docker-compose up

echo.
echo =====================================================================
echo Services stopped. Deployment complete.
echo =====================================================================
echo.
echo If you need to restart services, run: docker-compose up -d
echo Access points (when services are running):
echo   Frontend:                http://localhost:3000
echo   API Gateway:             http://localhost:8000
echo   Orchestration Service:   http://localhost:8010
echo.

pause
exit /b 0
:error_exit
echo [ERROR] Deployment failed >> "%LOG_FILE%"
type %LOG_FILE%
pause
exit /b 1
:end
endlocal
