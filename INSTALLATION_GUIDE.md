# 📥 KYC Agentic AI - Installation Guide

## Visual Overview

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     INSTALLATION FLOW DIAGRAM                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

                              START
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ System Requirements     │
                    │ Check (Prerequisites)   │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Docker Installation │
                    │ & Verification      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Clone/Setup Project │
                    │ Repository          │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Configure Project   │
                    │ (docker-compose)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Build Docker Images │
                    │ (9 containers)      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Start Services      │
                    │ (docker-compose up) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Verify Installation │
                    │ (Health Checks)     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Access Application  │
                    │ http://localhost... │
                    └──────────┬──────────┘
                               │
                               ▼
                              SUCCESS ✅
```

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [Docker Installation](#docker-installation)
4. [Project Setup](#project-setup)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Hardware Requirements

```
┌─────────────────────────────────────────────────┐
│         MINIMUM HARDWARE REQUIREMENTS           │
├─────────────────────────────────────────────────┤
│ CPU:        Dual-core processor (2 cores)      │
│ RAM:        4 GB minimum (8 GB recommended)    │
│ Disk Space: 3-4 GB free for Docker images      │
│ Network:    Internet connection for downloads  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│      RECOMMENDED HARDWARE SPECIFICATIONS        │
├─────────────────────────────────────────────────┤
│ CPU:        Quad-core or better                │
│ RAM:        8 GB or more                       │
│ Disk Space: 10 GB SSD (faster performance)     │
│ Network:    Gigabit Ethernet                   │
└─────────────────────────────────────────────────┘
```

### Software Requirements

```
┌──────────────────────────────────────────────────────┐
│        OPERATING SYSTEM COMPATIBILITY               │
├──────────────────────────────────────────────────────┤
│ ✅ Windows 10 or later (Pro, Enterprise, Home)      │
│ ✅ Windows 11                                       │
│ ✅ macOS 10.15 or later                            │
│ ✅ Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+)    │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│        REQUIRED SOFTWARE PACKAGES                   │
├──────────────────────────────────────────────────────┤
│ • Docker Desktop 4.0+                              │
│   └─ Includes Docker Engine & Docker Compose      │
│                                                   │
│ • Git 2.25+                                       │
│   └─ For cloning repository                      │
│                                                   │
│ • PowerShell 5.1+ (Windows)                       │
│   └─ For running deployment scripts              │
│                                                   │
│ • Bash 4.0+ (Linux/macOS)                         │
│   └─ For running shell scripts                   │
└──────────────────────────────────────────────────────┘
```

### Network Ports

```
┌─────────────────────────────────────────────┐
│      REQUIRED AVAILABLE PORTS               │
├─────────────────────────────────────────────┤
│ Port 3000    │ Frontend Web UI              │
│ Port 8000    │ API Gateway                  │
│ Port 8001    │ Extract Agent                │
│ Port 8002    │ Verify Agent                 │
│ Port 8003    │ Reason Agent                 │
│ Port 8004    │ Risk Agent                   │
│ Port 8005    │ Decision Agent               │
│ Port 8010    │ Orchestration Service        │
│ Port 11434   │ Ollama LLM Service           │
└─────────────────────────────────────────────┘

If any port is in use, you'll need to:
1. Modify docker-compose.yml port mappings
2. OR kill the process using that port
3. OR change the deployment script
```

---

## 🔧 Step-by-Step Installation

### Step 1: Verify System Prerequisites

#### Windows:
```powershell
# Check Windows version
[System.Environment]::OSVersion

# Check available disk space
Get-Volume | Select-Object DriveLetter, Size, SizeRemaining

# Check RAM
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
```

#### Linux/macOS:
```bash
# Check OS version
uname -a

# Check disk space
df -h /

# Check RAM
free -h  # Linux
vm_stat  # macOS
```

### Step 2: Install Docker Desktop

#### Windows Installation

```
1. Download Docker Desktop
   → Visit: https://www.docker.com/products/docker-desktop
   → Click: "Download for Windows"
   → Choose: Windows 10 Pro or Windows 11

2. Run Installer
   → Double-click: Docker Desktop Installer.exe
   → Accept Terms and Conditions
   → Select: "Use WSL 2 instead of Hyper-V" (recommended)

3. Complete Installation
   → Click: "Install"
   → Wait for installation to complete
   → Restart computer when prompted

4. Start Docker Desktop
   → Search: "Docker Desktop" in Windows Start Menu
   → Click: "Docker Desktop"
   → Wait for Docker icon to appear in system tray
   → Status should show "Docker is running"

5. Verify Installation
   PowerShell:
   docker --version
   docker-compose --version
   
   Expected Output:
   Docker version 24.0.0+
   docker-compose version 2.0.0+
```

#### Linux Installation (Ubuntu)

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### macOS Installation

```bash
# Using Homebrew (recommended)
brew install docker

# Or download from:
# https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

### Step 3: Clone Project Repository

```bash
# Navigate to desired location
cd "C:\path\to\projects"  # Windows
# OR
cd ~/projects  # Linux/macOS

# Clone repository
git clone https://github.com/JoydipBhowmik-IBM/kyc-agentic-ai.git

# Navigate to project
cd kyc-agentic-ai

# Verify project structure
ls -la  # Linux/macOS
dir     # Windows PowerShell
```

### Step 4: Configure Environment

```bash
# Navigate to project root
cd kyc-agentic-ai

# Check if .env file exists
ls .env  # If not found, create one

# Create .env if needed
cat > .env << EOF
# Environment Variables
DEBUG=false
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
EOF

# Verify docker-compose.yml
cat docker-compose.yml
```

### Step 5: Build Docker Images

#### Option A: Using Deployment Script

```bash
# Navigate to project
cd kyc-agentic-ai

# Windows: Double-click
deploy.bat

# Linux/macOS:
bash rebuild.sh
# OR
./deploy.sh
```

#### Option B: Manual Docker Compose

```bash
# Build all images (fresh, no cache)
docker-compose build --no-cache

# Build with progress output
docker-compose build --no-cache --progress=plain

# Build specific service (if needed)
docker-compose build --no-cache extract-agent
```

### Step 6: Start Services

#### Option A: Using Deployment Script

```bash
# All-in-one deployment
cd kyc-agentic-ai
deploy.bat  # Windows
./deploy.sh # Linux/macOS
```

#### Option B: Manual Docker Compose

```bash
# Start all services in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d extract-agent

# Check service status
docker-compose ps
```

---

## 🚀 Deployment Scripts Installation

### Deploy.bat Installation (Windows)

```
Location: C:\Users\USERNAME\kyc-agentic-ai\deploy.bat

What it does:
1. Stops old containers      (2 minutes)
2. Builds Docker images      (10-15 minutes)
3. Starts all services       (1 minute)
4. Waits for initialization  (1 minute)
5. Shows status & URLs       (displays results)

Total Time: 10-15 minutes (first run)
            2-5 minutes (subsequent runs)

To Run:
→ Double-click deploy.bat
→ Follow console output
→ Wait for "DEPLOYMENT COMPLETED SUCCESSFULLY!"
```

---

## ✅ Verification

### Service Health Checks

```bash
# Check all containers
docker-compose ps

# Expected output:
# NAME                    STATUS
# kyc-frontend            Up (healthy)
# kyc-api-gateway         Up (healthy)
# kyc-extract-agent       Up (healthy)
# kyc-verify-agent        Up (healthy)
# kyc-reason-agent        Up (healthy)
# kyc-risk-agent          Up (healthy)
# kyc-decision-agent      Up (healthy)
# kyc-orchestration       Up (healthy)
# kyc-ollama              Up (healthy)
```

### API Health Endpoints

```bash
# API Gateway
curl http://localhost:8000/health

# Extract Agent
curl http://localhost:8001/health

# Verify Agent
curl http://localhost:8002/health

# Reason Agent
curl http://localhost:8003/health

# Risk Agent
curl http://localhost:8004/health

# Decision Agent
curl http://localhost:8005/health

# Orchestration Service
curl http://localhost:8010/health

# Expected Response:
# {"status": "healthy"}
```

### Web Interface Access

```
Open in Browser:
http://localhost:3000

Expected: KYC Application Web Interface loads
Status: Application ready for testing
```

---

## 🔍 Installation Verification Checklist

```
PRE-INSTALLATION
□ Windows 10/11 or Linux/macOS
□ 4GB+ RAM available
□ 3-4GB free disk space
□ All required ports available

POST-DOCKER-INSTALLATION
□ docker --version returns version info
□ docker-compose --version returns version info
□ Docker Desktop shows running status

POST-PROJECT-SETUP
□ Project folder contains all files
□ docker-compose.yml is present
□ All agent folders present

POST-BUILD
□ All 9 Docker images built successfully
□ No build errors in console

POST-DEPLOYMENT
□ All 9 containers running (docker-compose ps)
□ All health endpoints responding
□ Frontend accessible at http://localhost:3000

READY FOR USE
□ Application interface loads
□ All services operational
□ Ready for KYC testing
```

---

## ⚠️ Troubleshooting

### Problem: Docker Not Starting

**Symptom:** "Cannot connect to Docker daemon"

```
Solution:
1. Start Docker Desktop (Windows/macOS)
   → Search: Docker Desktop
   → Click: Docker Desktop
   → Wait for icon in system tray

2. Check Docker status
   docker ps
   
3. If still fails, restart Docker
   → Quit Docker Desktop completely
   → Wait 10 seconds
   → Reopen Docker Desktop
```

### Problem: Port Already in Use

**Symptom:** "Port 3000 already allocated"

```
Solution:
1. Find process using port (Windows PowerShell)
   netstat -ano | findstr :3000

2. Kill the process
   taskkill /PID <PID> /F

3. Or modify docker-compose.yml
   Change: "3000:3000"
   To:     "3001:3000"

4. Restart deployment
   docker-compose down
   docker-compose up -d
```

### Problem: Build Fails

**Symptom:** "Build failed" or error during docker-compose build

```
Solution:
1. Clean Docker system
   docker system prune -a

2. Clear cache
   docker builder prune

3. Try building again
   docker-compose build --no-cache

4. Check disk space
   Windows: Check C: drive free space
   Linux: df -h /
```

### Problem: Container Won't Start

**Symptom:** "Container exited" or "unhealthy"

```
Solution:
1. Check logs
   docker logs kyc-extract-agent

2. View detailed logs
   docker-compose logs -f extract-agent

3. Restart container
   docker-compose restart extract-agent

4. Rebuild service
   docker-compose build --no-cache extract-agent
   docker-compose up -d extract-agent
```

### Problem: Low Disk Space

**Symptom:** "Insufficient space" or build fails

```
Solution:
1. Clean up Docker
   docker system prune -a --volumes

2. Check free space
   Windows: Get-Volume C:
   Linux: df -h /

3. Free up space
   Delete unused files/folders
   Increase disk partition

4. Try deployment again
```

---

## 📊 Installation Summary

### Installation Steps Overview

```
Step 1: System Check          ✓ 2 minutes
Step 2: Docker Installation   ✓ 10 minutes
Step 3: Clone Repository      ✓ 2 minutes
Step 4: Configure Project     ✓ 1 minute
Step 5: Build Images          ✓ 10-15 minutes
Step 6: Start Services        ✓ 2-5 minutes
Step 7: Verify Installation   ✓ 2 minutes

TOTAL TIME: 30-40 minutes (first installation)
            2-5 minutes (subsequent deployments)
```

### What You'll Have After Installation

```
✅ Docker running on your system
✅ 9 Docker containers deployed
✅ All microservices operational
✅ Web interface accessible
✅ API endpoints available
✅ Ready for KYC application testing
✅ Deployment scripts for future updates
```

---

## 🎉 Installation Complete!

After successful installation, you will have:

1. **Running Application**
   - Access at: http://localhost:3000
   - Full KYC application interface

2. **Operational Services**
   - 9 microservices running
   - All health checks passing
   - APIs responding to requests

3. **Management Tools**
   - Deployment scripts
   - Monitoring utilities
   - Troubleshooting guides

4. **Documentation**
   - Complete guides
   - Troubleshooting references
   - Architecture documentation

---

## 📞 Next Steps

1. **Verify Installation**
   ```bash
   docker-compose ps
   curl http://localhost:3000
   ```

2. **Run Tests**
   - Upload sample KYC documents
   - Verify document processing
   - Check agent responses

3. **Explore Application**
   - Navigate web interface
   - Test different document types
   - Monitor service performance

4. **Read Architecture**
   - See ARCHITECTURE.md
   - Understand service communication
   - Review system design

---

**Installation Guide Version:** 1.0  
**Last Updated:** March 23, 2026  
**Status:** ✅ Production Ready

