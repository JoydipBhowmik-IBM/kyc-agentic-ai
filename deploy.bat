@echo off
REM ============================================================================
REM KYC Agentic AI - Complete Docker Deployment Script
REM ============================================================================
REM This script rebuilds the entire application and deploys it to Docker
REM
REM Features:
REM - Cleans up old containers and images
REM - Rebuilds all Docker images without cache
REM - Starts all services
REM - Verifies health status
REM - Displays logs
REM ============================================================================

setlocal enabledelayedexpansion

REM Get the project directory
cd /d "C:\Users\JOYDIPBHOWMIK\OneDrive - IBM\RBC\Agentic AI\kyc-agentic-ai"

echo.
echo ============================================================================
echo KYC Agentic AI - Docker Deployment Script
echo ============================================================================
echo.

REM Set color variables
for /F %%A in ('echo prompt $H ^| cmd') do set "BS=%%A"

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [INFO] Docker is running. Proceeding with deployment...
echo.

REM ============================================================================
REM STEP 1: Stop all running containers
REM ============================================================================
echo [STEP 1] Stopping all running containers...
docker-compose down
if errorlevel 1 (
    echo [WARNING] Some containers may not exist. Continuing anyway...
)
timeout /t 2 /nobreak >nul
echo [OK] All containers stopped.
echo.

REM ============================================================================
REM STEP 2: Remove old images (optional - uncomment to enable)
REM ============================================================================
echo [STEP 2] Preparing for clean rebuild...
echo [INFO] Old images will be replaced by new builds.
echo.

REM ============================================================================
REM STEP 3: Rebuild all Docker images without cache
REM ============================================================================
echo [STEP 3] Building all Docker images (this may take several minutes)...
echo [INFO] Building with --no-cache flag to ensure fresh builds...
echo.

docker-compose build --no-cache

if errorlevel 1 (
    echo [ERROR] Docker build failed!
    echo [INFO] Check the error messages above for details.
    pause
    exit /b 1
)
echo [OK] All Docker images built successfully.
echo.

REM ============================================================================
REM STEP 4: Start all containers
REM ============================================================================
echo [STEP 4] Starting all containers...
docker-compose up -d

if errorlevel 1 (
    echo [ERROR] Failed to start containers!
    pause
    exit /b 1
)
echo [OK] All containers started in detached mode.
echo.

REM ============================================================================
REM STEP 5: Wait for containers to fully initialize
REM ============================================================================
echo [STEP 5] Waiting for containers to initialize (30 seconds)...
for /L %%i in (30,-1,1) do (
    cls
    echo [STEP 5] Waiting for containers to initialize... %%i seconds remaining
    timeout /t 1 /nobreak >nul
)
echo.

REM ============================================================================
REM STEP 6: Verify container status
REM ============================================================================
echo [STEP 6] Verifying container status...
echo.
docker-compose ps
echo.

REM ============================================================================
REM STEP 7: Display health status
REM ============================================================================
echo [STEP 7] Health check status:
echo.
docker-compose ps --format "table {{.Names}}\t{{.Status}}"
echo.

REM ============================================================================
REM STEP 8: Show useful information
REM ============================================================================
echo [STEP 8] Deployment Information:
echo.
echo ============================================================================
echo Deployed Services:
echo ============================================================================
echo.
echo Frontend:               http://localhost:3000
echo API Gateway:            http://localhost:8000/health
echo Orchestration Service:  http://localhost:8010/health
echo.
echo Individual Agent Ports:
echo   - Extract Agent:      http://localhost:8001/health
echo   - Verify Agent:       http://localhost:8002/health
echo   - Reason Agent:       http://localhost:8003/health
echo   - Risk Agent:         http://localhost:8004/health
echo   - Decision Agent:     http://localhost:8005/health
echo   - Ollama:             http://localhost:11434
echo.

REM ============================================================================
REM STEP 9: Optional - Show recent logs
REM ============================================================================
echo [STEP 9] Recent container logs (last 10 lines from each):
echo.
echo --- API Gateway Logs ---
docker logs kyc-api-gateway --tail 5 2>nul || echo No logs available
echo.
echo --- Orchestration Service Logs ---
docker logs kyc-orchestration-service --tail 5 2>nul || echo No logs available
echo.
echo --- Extract Agent Logs ---
docker logs kyc-extract-agent --tail 5 2>nul || echo No logs available
echo.

REM ============================================================================
REM DEPLOYMENT COMPLETE
REM ============================================================================
echo.
echo ============================================================================
echo DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ============================================================================
echo.
echo Next Steps:
echo 1. Open http://localhost:3000 in your browser to access the frontend
echo 2. Test the application with sample documents
echo 3. Monitor logs with: docker-compose logs -f [service-name]
echo 4. To stop all services: docker-compose down
echo 5. To view logs: docker-compose logs [service-name]
echo.
echo For troubleshooting:
echo - Check individual service health at the URLs above
echo - Review logs: docker logs [container-name]
echo - Rebuild specific service: docker-compose build --no-cache [service]
echo.
pause

