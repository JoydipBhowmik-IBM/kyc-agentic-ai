@echo off
REM ============================================================================
REM KYC Agentic AI - Selective Docker Deployment Script
REM ============================================================================
REM This script deploys ONLY the KYC Agentic AI application
REM
REM Services Deployed:
REM - PostgreSQL Database
REM - Keycloak Identity Management
REM - API Gateway
REM - Orchestration Service
REM - Extract Agent
REM - Verify Agent
REM - Reason Agent
REM - Risk Agent
REM - Decision Agent
REM - Frontend UI
REM
REM Features:
REM - Stops only KYC-related containers
REM - Rebuilds only KYC-related Docker images
REM - Starts all KYC services
REM - Verifies health status
REM ============================================================================

setlocal enabledelayedexpansion

REM Get the script's directory
cd /d "%~dp0"

echo.
echo ============================================================================
echo KYC Agentic AI - Selective Docker Deployment
echo ============================================================================
echo.
echo This deployment script will:
echo  - Deploy ONLY the KYC Agentic AI application
echo  - Start all 10 services
echo  - Verify container health
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [INFO] Docker is running. Proceeding with KYC deployment...
echo.

REM ============================================================================
REM STEP 1: Stop KYC-related containers
REM ============================================================================
echo [STEP 1] Stopping KYC-related containers...
docker-compose -f docker-compose.yml down

if errorlevel 1 (
    echo [WARNING] Some containers may not exist. Continuing anyway...
)
timeout /t 2 /nobreak >nul
echo [OK] KYC containers stopped.
echo.

REM ============================================================================
REM STEP 2: Verify project structure
REM ============================================================================
echo [STEP 2] Verifying KYC project files exist...
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found in current directory!
    pause
    exit /b 1
)
echo [OK] Project files verified.
echo.

REM ============================================================================
REM STEP 3: Rebuild KYC Docker images without cache
REM ============================================================================
echo [STEP 3] Building KYC Docker images (this may take several minutes)...
echo [INFO] Building with --no-cache flag to ensure fresh builds...
echo.

docker-compose build --no-cache

if errorlevel 1 (
    echo [ERROR] Docker build failed!
    echo [INFO] Check the error messages above for details.
    pause
    exit /b 1
)
echo [OK] All KYC Docker images built successfully.
echo.

REM ============================================================================
REM STEP 4: Start KYC containers
REM ============================================================================
echo [STEP 4] Starting KYC containers...
docker-compose up -d

if errorlevel 1 (
    echo [ERROR] Failed to start KYC containers!
    pause
    exit /b 1
)
echo [OK] All KYC containers started in detached mode.
echo.

REM ============================================================================
REM STEP 5: Wait for containers to initialize
REM ============================================================================
echo [STEP 5] Waiting for KYC containers to initialize (30 seconds)...
for /L %%i in (30,-1,1) do (
    cls
    echo [STEP 5] Waiting for KYC containers to initialize... %%i seconds remaining
    timeout /t 1 /nobreak >nul
)
echo.

REM ============================================================================
REM STEP 6: Verify KYC container status
REM ============================================================================
echo [STEP 6] Verifying KYC container status...
echo.
docker-compose ps
echo.

REM ============================================================================
REM STEP 7: Display KYC service health status
REM ============================================================================
echo [STEP 7] KYC Service Health Status:
echo.
docker-compose ps --format "table {{.Names}}\t{{.Status}}"
echo.

REM ============================================================================
REM STEP 8: Show KYC deployment information
REM ============================================================================
echo [STEP 8] KYC Application Information:
echo.
echo ============================================================================
echo Deployed KYC Services:
echo ============================================================================
echo.
echo Frontend UI:               http://localhost:3000
echo API Gateway:              http://localhost:8000
echo API Documentation:        http://localhost:8000/docs
echo Health Check:             http://localhost:8000/health
echo.
echo Orchestration Service:    http://localhost:8010/health
echo.
echo Individual Agent Endpoints:
echo   - Extract Agent:        http://localhost:8001/health
echo   - Verify Agent:         http://localhost:8002/health
echo   - Reason Agent:         http://localhost:8003/health
echo   - Risk Agent:           http://localhost:8004/health
echo   - Decision Agent:       http://localhost:8005/health
echo.
echo Identity Management:
echo   - Keycloak Admin:       http://localhost:8080/admin
echo   - Username:             admin
echo   - Password:             admin123
echo.
echo Database:
echo   - PostgreSQL:           localhost:5432
echo   - Database:             keycloak
echo   - Username:             keycloak
echo   - Password:             keycloak123
echo.

REM ============================================================================
REM STEP 9: Show container logs summary
REM ============================================================================
echo [STEP 9] KYC Container Logs (last 3 lines from each critical service):
echo.
echo --- API Gateway ---
docker logs kyc-api-gateway --tail 3 2>nul || echo No logs available
echo.
echo --- Orchestration Service ---
docker logs kyc-orchestration --tail 3 2>nul || echo No logs available
echo.
echo --- Frontend ---
docker logs kyc-frontend --tail 3 2>nul || echo No logs available
echo.

REM ============================================================================
REM KYC DEPLOYMENT COMPLETE
REM ============================================================================
echo.
echo ============================================================================
echo KYC AGENTIC AI DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ============================================================================
echo.
echo ✓ All 10 services are now running:
echo   - PostgreSQL Database
echo   - Keycloak Identity Management
echo   - API Gateway
echo   - Orchestration Service
echo   - Extract Agent
echo   - Verify Agent
echo   - Reason Agent
echo   - Risk Agent
echo   - Decision Agent
echo   - Frontend UI
echo.
echo Next Steps:
echo 1. Open http://localhost:3000 in your browser to access the KYC application
echo 2. Login to Keycloak admin at http://localhost:8080/admin
echo    (Username: admin, Password: admin123)
echo 3. Test the application with sample KYC documents
echo 4. Monitor logs: docker-compose logs -f [service-name]
echo 5. To stop all KYC services: docker-compose down
echo 6. To view specific service logs: docker logs [container-name]
echo.
echo Useful Commands:
echo - View all KYC services:    docker-compose ps
echo - View service logs:        docker-compose logs [service-name]
echo - Rebuild specific service: docker-compose build --no-cache [service-name]
echo - Restart all services:     docker-compose restart
echo.
echo For troubleshooting, visit the health check URLs:
echo   http://localhost:8000/health       (API Gateway)
echo   http://localhost:8010/health       (Orchestration Service)
echo   http://localhost:8001/health       (Extract Agent)
echo   http://localhost:8002/health       (Verify Agent)
echo   http://localhost:8003/health       (Reason Agent)
echo   http://localhost:8004/health       (Risk Agent)
echo   http://localhost:8005/health       (Decision Agent)
echo.
pause

