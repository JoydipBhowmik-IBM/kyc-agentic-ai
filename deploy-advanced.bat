@echo off
REM ============================================================================
REM KYC Agentic AI - Advanced Docker Deployment with Registry Push
REM ============================================================================
REM This script provides advanced deployment options including:
REM - Building Docker images
REM - Tagging images with version
REM - Pushing to Docker registry (Docker Hub or private registry)
REM - Deploying to local Docker
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "C:\Users\JOYDIPBHOWMIK\OneDrive - IBM\RBC\Agentic AI\kyc-agentic-ai"

echo.
echo ============================================================================
echo KYC Agentic AI - Advanced Docker Deployment
echo ============================================================================
echo.

REM Check Docker
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    pause
    exit /b 1
)

REM Get deployment options
echo Please select deployment option:
echo.
echo 1. Local Deployment (build and deploy locally only)
echo 2. Docker Hub Push (build, tag, push to Docker Hub, then deploy locally)
echo 3. Custom Registry Push (build, tag, push to custom registry, then deploy locally)
echo 4. View current deployment status
echo 5. Stop all containers
echo 6. View logs
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto LOCAL_DEPLOY
if "%choice%"=="2" goto HUB_DEPLOY
if "%choice%"=="3" goto CUSTOM_DEPLOY
if "%choice%"=="4" goto STATUS
if "%choice%"=="5" goto STOP
if "%choice%"=="6" goto LOGS
goto END

REM ============================================================================
REM LOCAL DEPLOYMENT
REM ============================================================================
:LOCAL_DEPLOY
echo.
echo [DEPLOYING LOCALLY]
echo.
echo Stopping existing containers...
docker-compose down
timeout /t 2 /nobreak >nul
echo.
echo Building all Docker images (no cache)...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo.
echo Starting containers...
docker-compose up -d
echo.
echo Waiting for containers to initialize (20 seconds)...
for /L %%i in (20,-1,1) do (
    cls
    echo Waiting... %%i seconds remaining
    timeout /t 1 /nobreak >nul
)
echo.
echo [OK] Deployment complete!
docker-compose ps
echo.
pause
goto END

REM ============================================================================
REM DOCKER HUB DEPLOYMENT
REM ============================================================================
:HUB_DEPLOY
echo.
echo [DOCKER HUB DEPLOYMENT]
echo.
set /p registry_user="Enter Docker Hub username: "
set /p image_version="Enter image version tag (e.g., 1.0.0, latest): "
if "%image_version%"=="" set "image_version=latest"
echo.
echo Building all images locally...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo.
echo Tagging images for Docker Hub...
docker tag kyc-agentic-ai-frontend:latest %registry_user%/kyc-frontend:%image_version%
docker tag kyc-agentic-ai-api-gateway:latest %registry_user%/kyc-api-gateway:%image_version%
docker tag kyc-agentic-ai-orchestration-service:latest %registry_user%/kyc-orchestration-service:%image_version%
docker tag kyc-agentic-ai-extract-agent:latest %registry_user%/kyc-extract-agent:%image_version%
docker tag kyc-agentic-ai-verify-agent:latest %registry_user%/kyc-verify-agent:%image_version%
docker tag kyc-agentic-ai-reason-agent:latest %registry_user%/kyc-reason-agent:%image_version%
docker tag kyc-agentic-ai-risk-agent:latest %registry_user%/kyc-risk-agent:%image_version%
docker tag kyc-agentic-ai-decision-agent:latest %registry_user%/kyc-decision-agent:%image_version%
echo.
echo Images tagged successfully!
echo.
set /p push_confirm="Do you want to push to Docker Hub? (y/n): "
if /i "%push_confirm%"=="y" (
    echo.
    echo Pushing images to Docker Hub...
    docker push %registry_user%/kyc-frontend:%image_version%
    docker push %registry_user%/kyc-api-gateway:%image_version%
    docker push %registry_user%/kyc-orchestration-service:%image_version%
    docker push %registry_user%/kyc-extract-agent:%image_version%
    docker push %registry_user%/kyc-verify-agent:%image_version%
    docker push %registry_user%/kyc-reason-agent:%image_version%
    docker push %registry_user%/kyc-risk-agent:%image_version%
    docker push %registry_user%/kyc-decision-agent:%image_version%
    echo [OK] Images pushed to Docker Hub!
)
echo.
echo Starting local deployment...
docker-compose down
timeout /t 2 /nobreak >nul
docker-compose up -d
echo.
echo Waiting for containers (20 seconds)...
for /L %%i in (20,-1,1) do (
    cls
    echo Waiting... %%i seconds remaining
    timeout /t 1 /nobreak >nul
)
echo.
echo [OK] Local deployment running!
docker-compose ps
echo.
pause
goto END

REM ============================================================================
REM CUSTOM REGISTRY DEPLOYMENT
REM ============================================================================
:CUSTOM_DEPLOY
echo.
echo [CUSTOM REGISTRY DEPLOYMENT]
echo.
set /p registry_url="Enter custom registry URL (e.g., registry.example.com): "
set /p registry_repo="Enter repository path (e.g., myproject): "
set /p image_version="Enter image version tag (e.g., 1.0.0, latest): "
if "%image_version%"=="" set "image_version=latest"
echo.
echo Building all images locally...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo.
echo Tagging images for custom registry...
docker tag kyc-agentic-ai-frontend:latest %registry_url%/%registry_repo%/kyc-frontend:%image_version%
docker tag kyc-agentic-ai-api-gateway:latest %registry_url%/%registry_repo%/kyc-api-gateway:%image_version%
docker tag kyc-agentic-ai-orchestration-service:latest %registry_url%/%registry_repo%/kyc-orchestration-service:%image_version%
docker tag kyc-agentic-ai-extract-agent:latest %registry_url%/%registry_repo%/kyc-extract-agent:%image_version%
docker tag kyc-agentic-ai-verify-agent:latest %registry_url%/%registry_repo%/kyc-verify-agent:%image_version%
docker tag kyc-agentic-ai-reason-agent:latest %registry_url%/%registry_repo%/kyc-reason-agent:%image_version%
docker tag kyc-agentic-ai-risk-agent:latest %registry_url%/%registry_repo%/kyc-risk-agent:%image_version%
docker tag kyc-agentic-ai-decision-agent:latest %registry_url%/%registry_repo%/kyc-decision-agent:%image_version%
echo.
echo Images tagged successfully!
echo.
set /p push_confirm="Do you want to push to %registry_url%? (y/n): "
if /i "%push_confirm%"=="y" (
    echo.
    echo Pushing images to custom registry...
    docker push %registry_url%/%registry_repo%/kyc-frontend:%image_version%
    docker push %registry_url%/%registry_repo%/kyc-api-gateway:%image_version%
    docker push %registry_url%/%registry_repo%/kyc-orchestration-service:%image_version%
    docker push %registry_url%/%registry_repo%/kyc-extract-agent:%image_version%
    docker push %registry_url%/%registry_repo%/kyc-verify-agent:%image_version%
    docker push %registry_url%/%registry_repo%/kyc-reason-agent:%image_version%
    docker push %registry_url%/%registry_repo%/kyc-risk-agent:%image_version%
    docker push %registry_url%/%registry_repo%/kyc-decision-agent:%image_version%
    echo [OK] Images pushed to custom registry!
)
echo.
echo Starting local deployment...
docker-compose down
timeout /t 2 /nobreak >nul
docker-compose up -d
echo.
echo Waiting for containers (20 seconds)...
for /L %%i in (20,-1,1) do (
    cls
    echo Waiting... %%i seconds remaining
    timeout /t 1 /nobreak >nul
)
echo.
echo [OK] Local deployment running!
docker-compose ps
echo.
pause
goto END

REM ============================================================================
REM DEPLOYMENT STATUS
REM ============================================================================
:STATUS
echo.
echo [CURRENT DEPLOYMENT STATUS]
echo.
docker-compose ps
echo.
pause
goto END

REM ============================================================================
REM STOP DEPLOYMENT
REM ============================================================================
:STOP
echo.
echo Stopping all containers...
docker-compose down
echo [OK] All containers stopped.
echo.
pause
goto END

REM ============================================================================
REM VIEW LOGS
REM ============================================================================
:LOGS
echo.
echo Available services:
echo 1. api-gateway
echo 2. orchestration-service
echo 3. extract-agent
echo 4. verify-agent
echo 5. reason-agent
echo 6. risk-agent
echo 7. decision-agent
echo 8. frontend
echo 9. ollama
echo.
set /p service_num="Enter service number or name: "

if "%service_num%"=="1" set service=kyc-api-gateway
if "%service_num%"=="2" set service=kyc-orchestration-service
if "%service_num%"=="3" set service=kyc-extract-agent
if "%service_num%"=="4" set service=kyc-verify-agent
if "%service_num%"=="5" set service=kyc-reason-agent
if "%service_num%"=="6" set service=kyc-risk-agent
if "%service_num%"=="7" set service=kyc-decision-agent
if "%service_num%"=="8" set service=kyc-frontend
if "%service_num%"=="9" set service=kyc-ollama

if not defined service set service=%service_num%

echo.
echo Showing logs for %service%...
echo.
docker logs --tail 50 %service%
echo.
pause
goto END

:END
echo.
echo ============================================================================
echo Deployment script completed.
echo ============================================================================
echo.

