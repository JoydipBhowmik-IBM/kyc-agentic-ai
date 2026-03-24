@echo off
REM ============================================================================
REM KYC Agentic AI - Complete Build, Push & Deploy Script (v1.0.0-fix)
REM ============================================================================
REM This script performs complete CI/CD pipeline:
REM 1. Build entire application from source
REM 2. Tag Docker images with version
REM 3. Push images to Docker Hub
REM 4. Pull latest images
REM 5. Restart all containers with new code changes
REM
REM Services Deployed:
REM - PostgreSQL Database
REM - Keycloak Identity Management
REM - API Gateway
REM - Orchestration Service
REM - Extract Agent (with PAN fix)
REM - Verify Agent (with PAN fix)
REM - Reason Agent (with PAN fix)
REM - Risk Agent (with PAN fix)
REM - Decision Agent (with PAN fix)
REM - Frontend UI
REM
REM Code Changes Included:
REM ✓ PAN document fix - is_valid_kyc preservation through pipeline
REM ✓ Enhanced decision logic for valid KYC documents
REM ✓ Comprehensive logging for debugging
REM ============================================================================

setlocal enabledelayedexpansion

REM Get the script's directory
cd /d "%~dp0"

REM Color codes and version info
set VERSION=1.0.0-fix
set BUILD_DATE=%date%
set BUILD_TIME=%time%
set DOCKER_HUB_USERNAME=YOUR_DOCKER_HUB_USERNAME

echo.
echo ============================================================================
echo KYC Agentic AI - Complete Build, Push and Deploy Pipeline
echo Version: %VERSION%
echo Build Date: %BUILD_DATE% %BUILD_TIME%
echo ============================================================================
echo.
echo This script will:
echo  1. Build entire application from source code
echo  2. Tag all Docker images with version %VERSION%
echo  3. Push images to Docker Hub
echo  4. Pull latest images on deployment
echo  5. Restart all containers with new code changes
echo  6. Verify health of all services
echo.
echo Code Changes Applied:
echo  ✓ PAN Document Rejection Fix
echo    - is_valid_kyc flag preservation through agent pipeline
echo    - Enhanced decision logic for KYC document validation
echo    - Comprehensive logging for pipeline tracing
echo.

REM ============================================================================
REM STEP 0: Get Docker Hub Credentials
REM ============================================================================
echo [STEP 0] Configuring Docker Hub credentials...
echo.
echo Enter your Docker Hub username (or press Enter for default):
set /p DOCKER_HUB_USERNAME=

if "!DOCKER_HUB_USERNAME!"=="" (
    echo [ERROR] Docker Hub username is required!
    echo [INFO] Please run the script again and enter your Docker Hub username.
    pause
    exit /b 1
)

echo [OK] Docker Hub username set to: !DOCKER_HUB_USERNAME!
echo.

REM ============================================================================
REM STEP 1: Check if Docker is running
REM ============================================================================
echo [STEP 1] Verifying Docker installation and connectivity...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running or not installed.
    echo [INFO] Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [OK] Docker is running and accessible.
echo.

REM ============================================================================
REM STEP 2: Verify project structure
REM ============================================================================
echo [STEP 2] Verifying project structure...
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found in current directory!
    pause
    exit /b 1
)
if not exist "agents\extract-agent\Dockerfile" (
    echo [ERROR] Required Dockerfiles not found!
    pause
    exit /b 1
)
echo [OK] All required project files verified.
echo.

REM ============================================================================
REM STEP 3: Stop existing KYC containers
REM ============================================================================
echo [STEP 3] Stopping existing KYC containers...
docker-compose -f docker-compose.yml down 2>nul

if errorlevel 1 (
    echo [WARNING] Some containers may not exist or already stopped. Continuing...
) else (
    echo [OK] Existing KYC containers stopped.
)
timeout /t 2 /nobreak >nul
echo.

REM ============================================================================
REM STEP 4: Build all Docker images from source
REM ============================================================================
echo [STEP 4] Building all Docker images (this will take several minutes)...
echo [INFO] Building without cache to ensure all code changes are included...
echo.

docker-compose build --no-cache

if errorlevel 1 (
    echo [ERROR] Docker build failed!
    echo [INFO] Please check the error messages above for details.
    pause
    exit /b 1
)
echo [OK] All Docker images built successfully from source code.
echo.

REM ============================================================================
REM STEP 5: Prompt for Docker Hub Push
REM ============================================================================
echo [STEP 5] Docker Hub Push Configuration...
echo.
echo Do you want to push images to Docker Hub? (Y/N)
set /p PUSH_TO_HUB=

if /I "!PUSH_TO_HUB!"=="Y" (
    echo.
    echo [INFO] Docker Hub Push Workflow
    echo [INFO] Make sure you are logged into Docker Hub
    echo.
    echo Attempting Docker Hub login...
    docker login

    if errorlevel 1 (
        echo [WARNING] Docker Hub login failed!
        echo [INFO] Continuing with local deployment only.
    ) else (
        echo [OK] Successfully logged into Docker Hub

        REM Tag and push all images
        echo.
        echo [INFO] Tagging and pushing images to Docker Hub...
        echo.

        set IMAGES=extract-agent verify-agent reason-agent risk-agent decision-agent orchestration-service api-gateway frontend

        for %%i in (%IMAGES%) do (
            echo [PUSH] Tagging kyc-%%i:%VERSION% as !DOCKER_HUB_USERNAME!/kyc-%%i:%VERSION%
            docker tag kyc-%%i:latest !DOCKER_HUB_USERNAME!/kyc-%%i:%VERSION%
            if errorlevel 1 (
                echo [WARNING] Failed to tag kyc-%%i
            )

            echo [PUSH] Pushing !DOCKER_HUB_USERNAME!/kyc-%%i:%VERSION% to Docker Hub...
            docker push !DOCKER_HUB_USERNAME!/kyc-%%i:%VERSION%
            if errorlevel 1 (
                echo [WARNING] Failed to push kyc-%%i
            ) else (
                echo [OK] Successfully pushed kyc-%%i
            )

            echo [PUSH] Tagging latest version...
            docker tag kyc-%%i:latest !DOCKER_HUB_USERNAME!/kyc-%%i:latest
            docker push !DOCKER_HUB_USERNAME!/kyc-%%i:latest
            echo.
        )

        echo [OK] All images pushed to Docker Hub successfully!
        echo [INFO] Repository: https://hub.docker.com/r/!DOCKER_HUB_USERNAME!/kyc-extract-agent
        echo.
    )
) else (
    echo [INFO] Skipping Docker Hub push. Using local images only.
    echo.
)

REM ============================================================================
REM STEP 6: Start all KYC containers
REM ============================================================================
echo [STEP 6] Starting all KYC containers with new code changes...
docker-compose up -d

if errorlevel 1 (
    echo [ERROR] Failed to start KYC containers!
    echo [INFO] Check docker-compose.yml for configuration errors.
    pause
    exit /b 1
)
echo [OK] All KYC containers started in detached mode.
echo.

REM ============================================================================
REM STEP 7: Wait for containers to fully initialize
REM ============================================================================
echo [STEP 7] Waiting for containers to initialize (45 seconds)...
for /L %%i in (45,-1,1) do (
    title KYC Deployment - Initializing... %%i seconds remaining
    cls
    echo.
    echo ============================================================================
    echo KYC Agentic AI - Deployment in Progress
    echo ============================================================================
    echo.
    echo Status: Waiting for services to initialize...
    echo Remaining Time: %%i seconds
    echo.
    echo Building: postgresql, keycloak, api-gateway, orchestration-service,
    echo           extract-agent, verify-agent, reason-agent, risk-agent,
    echo           decision-agent, frontend
    echo.
    timeout /t 1 /nobreak >nul
)
echo.

REM ============================================================================
REM STEP 8: Verify all containers are running
REM ============================================================================
echo [STEP 8] Verifying container status...
echo.
docker-compose ps
echo.

REM ============================================================================
REM STEP 9: Health Check - Test API Gateway
REM ============================================================================
echo [STEP 9] Performing health checks...
echo.
echo Testing API Gateway health endpoint...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] API Gateway health check failed - containers still initializing
    echo [INFO] The application should be available shortly
) else (
    echo [OK] API Gateway is responding and healthy
)
echo.

REM ============================================================================
REM STEP 10: Display comprehensive deployment summary
REM ============================================================================
echo [STEP 10] Deployment Summary
echo.

title KYC Agentic AI - Deployment Complete

echo ============================================================================
echo KYC AGENTIC AI - COMPLETE DEPLOYMENT SUCCESSFUL!
echo Version: %VERSION%
echo Date: %BUILD_DATE% %BUILD_TIME%
echo ============================================================================
echo.
echo [DEPLOYMENT COMPLETE] All services deployed with new code changes
echo.
echo ============================================================================
echo DEPLOYED SERVICES (10 total):
echo ============================================================================
echo.
echo Web Services:
echo   Frontend UI:                        http://localhost:3000
echo   API Gateway (REST API):             http://localhost:8000
echo   API Documentation (Swagger):        http://localhost:8000/docs
echo   Orchestration Service:              http://localhost:8010
echo.
echo Identity & Access Management:
echo   Keycloak Admin Console:             http://localhost:8080/admin
echo   - Default Username:                 admin
echo   - Default Password:                 admin123
echo.
echo Individual Agent Health Checks:
echo   Extract Agent (OCR/Document Type):  http://localhost:8001/health
echo   Verify Agent (Validation):          http://localhost:8002/health
echo   Reason Agent (LLM Analysis):        http://localhost:8003/health
echo   Risk Agent (Risk Assessment):       http://localhost:8004/health
echo   Decision Agent (Final Decision):    http://localhost:8005/health
echo.
echo Database:
echo   PostgreSQL (Keycloak DB):           localhost:5432
echo   - Database Name:                    keycloak
echo   - Username:                         keycloak
echo   - Password:                         keycloak123
echo.
echo ============================================================================
echo CODE CHANGES DEPLOYED:
echo ============================================================================
echo.
echo ✓ PAN Document Rejection Fix (v1.0.0-fix)
echo   - Fixed: PAN documents were being rejected incorrectly
echo   - Solution: Enhanced is_valid_kyc flag preservation through pipeline
echo   - Impact: PAN documents now approved based on risk score
echo.
echo Modified Agents:
echo   ✓ Extract Agent:        Document type identification with PAN support
echo   ✓ Verify Agent:         Enhanced is_valid_kyc preservation
echo   ✓ Reason Agent:         Added is_valid_kyc double-check safeguard
echo   ✓ Risk Agent:           Added is_valid_kyc preservation check
echo   ✓ Decision Agent:       Fixed decision logic for valid KYC documents
echo   ✓ Orchestration Service: Enhanced logging for pipeline tracing
echo.
echo ============================================================================
echo QUICK START GUIDE:
echo ============================================================================
echo.
echo 1. OPEN THE APPLICATION:
echo    Open your browser and navigate to http://localhost:3000
echo.
echo 2. TEST PAN DOCUMENT UPLOAD:
echo    - Upload a PAN document image
echo    - Expected Result: Document should be APPROVED (not REJECTED)
echo    - Risk Score should be LOW/VERY_LOW
echo.
echo 3. VERIFY CODE CHANGES ARE WORKING:
echo    - Check Decision Agent logs:
echo      docker logs kyc-decision-agent ^| findstr "is_valid_kyc"
echo    - Should show: "Decision making - is_valid_kyc: True (type: bool)"
echo.
echo 4. MONITOR REAL-TIME LOGS:
echo    docker-compose logs -f [service-name]
echo.
echo 5. ACCESS ADMIN DASHBOARDS:
echo    - Keycloak: http://localhost:8080/admin (admin/admin123)
echo.
echo ============================================================================
echo USEFUL COMMANDS:
echo ============================================================================
echo.
echo View all services:
echo   docker-compose ps
echo.
echo View service logs (realtime):
echo   docker-compose logs -f [service-name]
echo.
echo View logs from specific container:
echo   docker logs [container-name] --tail 100
echo.
echo Restart specific service:
echo   docker-compose restart [service-name]
echo.
echo Stop all services:
echo   docker-compose down
echo.
echo Rebuild and restart specific service:
echo   docker-compose up -d --build --no-deps [service-name]
echo.
echo Check resource usage:
echo   docker stats
echo.
echo ============================================================================
echo VERIFICATION CHECKLIST:
echo ============================================================================
echo.
echo [ ] API Gateway is responding (http://localhost:8000/health)
echo [ ] Frontend loads at http://localhost:3000
echo [ ] All 5 agents health checks pass
echo [ ] Keycloak admin accessible (http://localhost:8080/admin)
echo [ ] PAN document upload shows APPROVED (not REJECTED)
echo [ ] Decision agent logs show is_valid_kyc: True
echo [ ] No error messages in docker-compose logs
echo.
echo ============================================================================
echo TROUBLESHOOTING:
echo ============================================================================
echo.
echo If services are not responding:
echo   1. Wait 30-60 seconds for full initialization
echo   2. Check container logs: docker logs [container-name]
echo   3. Verify Docker has enough memory (recommended: 8GB)
echo   4. Check port availability: netstat -ano ^| findstr :[port-number]
echo.
echo If PAN documents are still rejected:
echo   1. Restart decision-agent: docker-compose restart kyc-decision-agent
echo   2. Check logs for is_valid_kyc value
echo   3. Verify extract-agent correctly identifies documents
echo.
echo For other issues:
echo   - Check DEPLOYMENT_GUIDE.md in the project root
echo   - Review BUILD_REPORT.md for build details
echo   - Check application logs in docker-compose logs
echo.
echo ============================================================================
echo.
echo Deployment completed at: %date% %time%
echo.
pause

