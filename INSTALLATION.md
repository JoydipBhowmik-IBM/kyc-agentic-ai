# KYC/AML Agentic AI System - Installation Guide

**Document Version:** 1.0  
**Last Updated:** April 7, 2026

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
   - [Docker Compose (Recommended)](#docker-compose-recommended)
   - [Local Development Setup](#local-development-setup)
   - [Kubernetes Deployment](#kubernetes-deployment)
4. [Configuration](#configuration)
5. [Initialization](#initialization)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Post-Installation](#post-installation)

---

## System Requirements

### Minimum Hardware Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| CPU Cores | 4 | 8+ | LLM inference is CPU intensive |
| RAM | 16 GB | 32 GB | Ollama model requires 8-10 GB |
| Disk Space | 50 GB | 100 GB | For models, volumes, and logs |
| Network | 1 Gbps | 1 Gbps+ | For model downloads |

### Supported Operating Systems

- ✅ **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- ✅ **macOS**: 11.0+ (Intel and Apple Silicon)
- ✅ **Windows**: Windows 10 Pro/Enterprise, Windows Server 2019+

### Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Container orchestration |
| Git | 2.20+ | Version control |
| Python | 3.11+ | Backend services (local setup) |
| Node.js | 14.0+ | Frontend (local setup) |
| Curl | 7.6+ | Health checks and debugging |
| Tesseract OCR | 5.0+ | Document processing (optional for Docker) |

---

## Prerequisites

### 1. Check Docker Installation

```bash
# Check Docker version
docker --version
# Expected output: Docker version 20.10+

# Check Docker Compose version
docker-compose --version
# Expected output: Docker Compose version 2.0+

# Test Docker functionality
docker run hello-world
```

### 2. Verify System Limits

```bash
# Check file descriptor limits (Linux/macOS)
ulimit -n
# Should be >= 4096. If less, increase with:
ulimit -n 65536

# Check available memory
free -h          # Linux
vm_stat           # macOS
Get-ComputerInfo  # Windows PowerShell
```

### 3. Network Ports Availability

Verify these ports are available:

```bash
# Linux/macOS
netstat -tuln | grep LISTEN

# Windows PowerShell
netstat -ano | findstr LISTENING
```

**Required Ports:**

| Port | Service | Purpose |
|------|---------|---------|
| 3000 | Frontend | Web UI |
| 8000 | API Gateway | Main API entry point |
| 8003 | Reason Agent | RAG-based reasoning |
| 8004 | Risk Agent | Risk analysis |
| 8005 | Decision Agent | Final decisions |
| 8007 | Extract Agent | Document extraction |
| 8008 | Verify Agent | Verification rules |
| 8010 | Orchestration | Service coordinator |
| 8020 | MCP Server | Tool registry |
| 11434 | Ollama | LLM server |

---

## Installation Methods

---

## Docker Compose (Recommended)

### Step 1: Clone or Download the Repository

```bash
# Clone from Git
git clone https://github.com/your-org/kyc-agentic-ai.git
cd kyc-agentic-ai

# Or extract from archive
unzip kyc-agentic-ai.zip
cd kyc-agentic-ai
```

### Step 2: Prepare Configuration Files

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional - defaults work for local testing)
# nano .env          # Linux/macOS
# notepad .env       # Windows
```

**Default .env values:**

```dotenv
# KYC/AML Agentic AI - Environment Configuration
# Copy this file to .env and customize as needed
# The docker-compose.yml will automatically use these values

# =====================================================================
# Logging Configuration
# Default: WARNING (minimal logs - only errors and warnings)
# Options: DEBUG, INFO, WARNING, ERROR
# =====================================================================
LOG_LEVEL=WARNING

# =====================================================================
# Port Configuration
# Customize ports if defaults are already in use
# =====================================================================
EXTRACT_AGENT_PORT=8001
VERIFY_AGENT_PORT=8002
REASON_AGENT_PORT=8003
RISK_AGENT_PORT=8004
DECISION_AGENT_PORT=8005
API_GATEWAY_PORT=8000
FRONTEND_PORT=3000
ORCHESTRATION_PORT=8010
MCP_SERVER_PORT=8020

# =====================================================================
# LLM Configuration
# =====================================================================
OLLAMA_URL=http://ollama:11434
LLM_MODEL=mistral

# =====================================================================
# Frontend Configuration
# =====================================================================
NODE_ENV=production
API_GATEWAY_URL=http://localhost:8000

# =====================================================================
# Database Configuration
# =====================================================================
VECTOR_DB_PATH=/data/kyc_vector_db

# =====================================================================
# Service URLs (Internal - usually don't need modification)
# =====================================================================
# These are automatically set in docker-compose.yml
# But can be overridden if needed for custom networking

# Extract Agent (for other services)
# EXTRACT_AGENT_URL=http://extract-agent:8000
```

### Step 3: Initialize Vector Database

```bash
# On Linux/macOS
python3 init_vector_db_simple.py

# On Windows PowerShell
python init_vector_db_simple.py
```

**Expected output:**
```
═══════════════════════════════════════════════════════
Initializing KYC Vector Database (PAN-ONLY RULES)
═══════════════════════════════════════════════════════
Vector DB Path: ./kyc_vector_db
[✓] KYC rules initialized
[✓] Fraud patterns loaded
[✓] Vector database ready
```

### Step 4: Build and Start Services

```bash
# Build all Docker images
docker-compose build

# Start all services in background
docker-compose up -d

# View startup logs (may take 2-5 minutes)
docker-compose logs -f

# Wait for all services to be healthy
docker-compose ps
```

**Expected Status (all HEALTHY):**
```
NAME                    STATUS      PORTS
kyc-extract-agent       Up (healthy)    0.0.0.0:8007->8000/tcp
kyc-verify-agent        Up (healthy)    0.0.0.0:8008->8000/tcp
kyc-reason-agent        Up (healthy)    0.0.0.0:8003->8000/tcp
kyc-risk-agent          Up (healthy)    0.0.0.0:8004->8000/tcp
kyc-decision-agent      Up (healthy)    0.0.0.0:8005->8000/tcp
kyc-orchestration-service  Up (healthy) 0.0.0.0:8010->8010/tcp
kyc-api-gateway         Up (healthy)    0.0.0.0:8000->8000/tcp
kyc-frontend            Up (healthy)    0.0.0.0:3000->3000/tcp
kyc-mcp-server          Up (healthy)    0.0.0.0:8020->8020/tcp
kyc-ollama              Up (healthy)    0.0.0.0:11434->11434/tcp
```

### Step 5: Access the Application

Open your browser and navigate to:

```
http://localhost:3000
```

---

## Local Development Setup

For development without Docker, follow these steps:

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip python3-venv \
    nodejs npm tesseract-ocr tesseract-ocr-all \
    curl git imagemagick
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.11 node tesseract imagemagick

# Or using conda
conda create -n kyc python=3.11 nodejs
conda activate kyc
```

**Windows PowerShell:**
```powershell
# Using Chocolatey
choco install python nodejs tesseract imagemagick git -y

# Or download installers from official websites
# Python: https://www.python.org/downloads/
# Node.js: https://nodejs.org/
# Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
```

### Step 2: Set Up Virtual Environment

**Linux/macOS:**
```bash
# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate
```

**Windows PowerShell:**
```powershell
# Create Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Backend Dependencies

```bash
# Install all Python dependencies
pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install fastapi uvicorn requests pydantic python-multipart

# Install AI/ML components
pip install langchain langchain-ollama chromadb

# Install document processing
pip install pytesseract pillow

# Install analytics
pip install numpy scipy

# Or install from requirements.txt
pip install -r api-gateway/requirements.txt
pip install -r orchestration-service/requirements.txt
pip install -r agents/extract-agent/requirements.txt
pip install -r agents/verify-agent/requirements.txt
pip install -r agents/reason-agent/requirements.txt
pip install -r agents/risk-agent/requirements.txt
pip install -r agents/decision-agent/requirements.txt
pip install -r mcp-server/requirements.txt
```

### Step 4: Start Ollama Service

```bash
# Download and install Ollama
# https://ollama.ai

# Start Ollama service
ollama serve

# In another terminal, pull the Mistral model
ollama pull mistral

# Verify model is loaded
ollama list
```

### Step 5: Initialize Vector Database

```bash
python init_vector_db_simple.py
```

### Step 6: Start Backend Services

Open 8 terminal windows and start each service:

**Terminal 1: API Gateway**
```bash
cd api-gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2: Orchestration Service**
```bash
cd orchestration-service
uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

**Terminal 3: Extract Agent**
```bash
cd agents/extract-agent
uvicorn main:app --host 0.0.0.0 --port 8007 --reload
```

**Terminal 4: Verify Agent**
```bash
cd agents/verify-agent
uvicorn main:app --host 0.0.0.0 --port 8008 --reload
```

**Terminal 5: Reason Agent**
```bash
cd agents/reason-agent
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Terminal 6: Risk Agent**
```bash
cd agents/risk-agent
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

**Terminal 7: Decision Agent**
```bash
cd agents/decision-agent
uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

**Terminal 8: MCP Server**
```bash
cd mcp-server
uvicorn main:app --host 0.0.0.0 --port 8020 --reload
```

### Step 7: Start Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm start
```

### Step 8: Access Application

```
http://localhost:3000
```

---

## Kubernetes Deployment

### Prerequisites

- `kubectl` CLI installed
- Kubernetes cluster access (1.20+)
- Container registry access (Docker Hub, ECR, etc.)

### Step 1: Build and Push Docker Images

```bash
# Login to your container registry
docker login <your-registry>

# Build images for each service
docker build -t <registry>/kyc-extract-agent:1.0 ./agents/extract-agent
docker build -t <registry>/kyc-verify-agent:1.0 ./agents/verify-agent
docker build -t <registry>/kyc-reason-agent:1.0 ./agents/reason-agent
docker build -t <registry>/kyc-risk-agent:1.0 ./agents/risk-agent
docker build -t <registry>/kyc-decision-agent:1.0 ./agents/decision-agent
docker build -t <registry>/kyc-orchestration:1.0 ./orchestration-service
docker build -t <registry>/kyc-api-gateway:1.0 ./api-gateway
docker build -t <registry>/kyc-frontend:1.0 ./frontend
docker build -t <registry>/kyc-mcp-server:1.0 ./mcp-server

# Push all images
docker push <registry>/kyc-extract-agent:1.0
docker push <registry>/kyc-verify-agent:1.0
docker push <registry>/kyc-reason-agent:1.0
docker push <registry>/kyc-risk-agent:1.0
docker push <registry>/kyc-decision-agent:1.0
docker push <registry>/kyc-orchestration:1.0
docker push <registry>/kyc-api-gateway:1.0
docker push <registry>/kyc-frontend:1.0
docker push <registry>/kyc-mcp-server:1.0
```

### Step 2: Create Kubernetes Manifests

Create `k8s/` directory with manifest files:

```bash
mkdir -p k8s
```

**k8s/namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kyc-aml
```

**k8s/configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kyc-config
  namespace: kyc-aml
data:
  LOG_LEVEL: "WARNING"
  OLLAMA_URL: "http://ollama:11434"
  LLM_MODEL: "mistral"
```

**k8s/deployment.yaml:** (Example for API Gateway)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: kyc-aml
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: <registry>/kyc-api-gateway:1.0
        ports:
        - containerPort: 8000
        env:
        - name: ORCHESTRATION_SERVICE_URL
          value: "http://orchestration-service:8010"
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: kyc-config
              key: LOG_LEVEL
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Step 3: Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Deploy services
kubectl apply -f k8s/deployment.yaml

# Verify deployment
kubectl get pods -n kyc-aml
kubectl get svc -n kyc-aml

# Port-forward to access locally (testing)
kubectl port-forward -n kyc-aml svc/frontend 3000:3000
```

---

## Configuration

### Environment Variables

Create or edit `.env` file:

```bash
# KYC/AML Agentic AI - Environment Configuration
# Copy this file to .env and customize as needed
# The docker-compose.yml will automatically use these values

# =====================================================================
# Logging Configuration
# Default: WARNING (minimal logs - only errors and warnings)
# Options: DEBUG, INFO, WARNING, ERROR
# =====================================================================
LOG_LEVEL=WARNING

# =====================================================================
# Port Configuration
# Customize ports if defaults are already in use
# =====================================================================
EXTRACT_AGENT_PORT=8001
VERIFY_AGENT_PORT=8002
REASON_AGENT_PORT=8003
RISK_AGENT_PORT=8004
DECISION_AGENT_PORT=8005
API_GATEWAY_PORT=8000
FRONTEND_PORT=3000
ORCHESTRATION_PORT=8010
MCP_SERVER_PORT=8020

# =====================================================================
# LLM Configuration
# =====================================================================
OLLAMA_URL=http://ollama:11434
LLM_MODEL=mistral

# =====================================================================
# Frontend Configuration
# =====================================================================
NODE_ENV=production
API_GATEWAY_URL=http://localhost:8000

# =====================================================================
# Database Configuration
# =====================================================================
VECTOR_DB_PATH=/data/kyc_vector_db

# =====================================================================
# Service URLs (Internal - usually don't need modification)
# =====================================================================
# These are automatically set in docker-compose.yml
# But can be overridden if needed for custom networking

# Extract Agent (for other services)
# EXTRACT_AGENT_URL=http://extract-agent:8000
```

### Log Configuration

Adjust logging level in `.env`:

```bash
# Log Levels
LOG_LEVEL=DEBUG    # Most verbose - all messages
LOG_LEVEL=INFO     # Informational messages
LOG_LEVEL=WARNING  # Warnings and errors only (default)
LOG_LEVEL=ERROR    # Only errors
```

### Performance Tuning

**For production with high load:**

```bash
# Increase timeouts
REQUEST_TIMEOUT=600

# Scale workers (Docker Compose)
# Add to docker-compose.yml:
deploy:
  replicas: 3

# Increase Docker memory limits
# Add to docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
    reservations:
      memory: 2G
```

---

## Initialization

### Vector Database Initialization

The vector database is automatically initialized during Docker Compose startup. For manual initialization:

```bash
python init_vector_db_simple.py
```

This script:
- Creates `kyc_vector_db/` directory
- Initializes KYC rules (PAN format validation)
- Loads fraud patterns
- Creates vector indices

### Database Contents

**kyc_rules.json:**
- PAN document format validation rules
- Photo requirements
- Name field validation
- Expiry date checks

**fraud_patterns.json:**
- Known fraud indicators
- Suspicious keywords
- Red flag patterns

---

## Verification

### Health Checks

```bash
# Check API Gateway
curl http://localhost:8000/health

# Check each agent
curl http://localhost:8003/health  # Reason Agent
curl http://localhost:8004/health  # Risk Agent
curl http://localhost:8005/health  # Decision Agent
curl http://localhost:8007/health  # Extract Agent
curl http://localhost:8008/health  # Verify Agent
curl http://localhost:8010/health  # Orchestration
curl http://localhost:8020/health  # MCP Server

# Check Ollama
curl http://localhost:11434/api/health
```

### Test API Endpoints

```bash
# Test document upload (sample request)
curl -X POST -F "file=@sample_document.pdf" \
  http://localhost:8000/kyc

# View logs
docker-compose logs -f api-gateway
docker-compose logs -f orchestration-service

# Or check individual service
docker logs kyc-extract-agent
```

### Verify All Services

```bash
# Check service status
docker-compose ps

# All should show "Up (healthy)"
# If any are unhealthy, check logs:
docker-compose logs <service-name>
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Docker Daemon Not Running

**Error:**
```
Cannot connect to Docker daemon
```

**Solution:**
```bash
# Linux
sudo systemctl start docker

# macOS
open -a Docker

# Windows
# Start Docker Desktop from Applications
```

#### 2. Port Already in Use

**Error:**
```
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**
```bash
# Find what's using the port (Linux/macOS)
lsof -i :8000

# Find what's using the port (Windows PowerShell)
netstat -ano | findstr :8000

# Stop the service or use different port
docker-compose down
# Edit .env and change port
docker-compose up -d
```

#### 3. Out of Memory

**Error:**
```
Cannot allocate memory / OOMKilled
```

**Solution:**
```bash
# Check Docker memory allocation
docker stats

# Increase Docker memory limit:
# Docker Desktop → Preferences → Resources → Memory
# Allocate at least 16GB

# Or use resource limits in compose:
deploy:
  resources:
    limits:
      memory: 8G
```

#### 4. Ollama Model Not Loading

**Error:**
```
failed to connect to ollama service
```

**Solution:**
```bash
# Check Ollama status
docker logs ollama

# Manually pull model
docker exec ollama ollama pull mistral

# Check model is loaded
docker exec ollama ollama list

# Wait for full startup (can take 5+ minutes)
docker-compose logs -f ollama
```

#### 5. Service Dependency Issues

**Error:**
```
Service unreachable / Connection refused
```

**Solution:**
```bash
# Check service startup order
docker-compose logs

# Restart services with dependencies
docker-compose down
docker volume prune  # Optional: clean volumes
docker-compose up -d

# Wait for all health checks (2-5 minutes)
watch docker-compose ps
```

#### 6. Vector Database Not Initialized

**Error:**
```
Vector DB path not found / No rules loaded
```

**Solution:**
```bash
# Re-initialize vector database
python init_vector_db_simple.py

# Or manually initialize in Docker
docker-compose exec vector-db-init bash
python init_vector_db_simple.py

# Check volume
docker volume ls | grep kyc-vector-db
docker volume inspect kyc_vector_db
```

#### 7. Tesseract OCR Not Found

**Error:**
```
TesseractNotFoundError: tesseract is not installed
```

**Solution:**
```bash
# Linux
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# If using Docker (included automatically)
# Verify: docker-compose exec extract-agent which tesseract
```

#### 8. Frontend Won't Connect to API

**Error:**
```
CORS error / API unreachable
```

**Solution:**
```bash
# Check API Gateway is running
curl http://localhost:8000/health

# Check frontend configuration
docker-compose logs frontend

# Verify environment variables
docker-compose exec frontend printenv | grep API

# Update API_GATEWAY_URL in .env
API_GATEWAY_URL=http://localhost:8000
docker-compose up -d frontend
```

### Debug Mode

Enable verbose logging:

```bash
# Set debug level
export LOG_LEVEL=DEBUG
docker-compose up -d

# View logs with timestamps
docker-compose logs -f --timestamps

# Or specific service
docker-compose logs -f --timestamps api-gateway
```

### Health Check Diagnostics

```bash
# Full system health check script
#!/bin/bash
echo "=== KYC/AML System Health Check ==="

services=(
  "8000:api-gateway"
  "8003:reason-agent"
  "8004:risk-agent"
  "8005:decision-agent"
  "8007:extract-agent"
  "8008:verify-agent"
  "8010:orchestration"
  "8020:mcp-server"
  "11434:ollama"
  "3000:frontend"
)

for service in "${services[@]}"; do
  port="${service%:*}"
  name="${service#*:}"
  if curl -s http://localhost:$port/health > /dev/null 2>&1; then
    echo "✓ $name ($port) - HEALTHY"
  else
    echo "✗ $name ($port) - UNHEALTHY"
  fi
done
```

---

## Post-Installation

### 1. Verify Installation

```bash
# All containers running
docker-compose ps

# All health checks passing
curl http://localhost:8000/health

# Frontend accessible
curl http://localhost:3000
```

### 2. Test with Sample Document

1. Navigate to `http://localhost:3000`
2. Click "Upload Document"
3. Select a test KYC document (ID, passport, etc.)
4. View processing results

### 3. Configure for Production

**Essential Steps:**

```bash
# 1. Update environment for production
LOG_LEVEL=WARNING
NODE_ENV=production

# 2. Set up reverse proxy (Nginx/Kong)
# 3. Enable HTTPS/TLS
# 4. Configure authentication/authorization
# 5. Set up centralized logging
# 6. Configure backup/persistence

# 7. Scale services as needed
docker-compose up -d --scale extract-agent=3 --scale reason-agent=2

# 8. Set up monitoring
# - Prometheus for metrics
# - Grafana for dashboards
# - ELK for log aggregation
```

### 4. Backup Configuration

```bash
# Backup volumes
docker-compose exec -T vector-db-init tar czf - /data/kyc_vector_db > backup.tar.gz

# Backup environment
cp .env .env.backup

# Backup application state
docker run --rm -v kyc_vector_db:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/kyc_backup.tar.gz /data
```

### 5. Backup and Restore Procedures

**Backup:**
```bash
# Create timestamped backup
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup volumes
docker run --rm -v kyc_vector_db:/data -v $(pwd)/$BACKUP_DIR:/backup \
  ubuntu tar czf /backup/vector_db.tar.gz /data

# Backup compose configuration
cp docker-compose.yml $BACKUP_DIR/
cp .env $BACKUP_DIR/
```

**Restore:**
```bash
# Restore from backup
docker run --rm -v kyc_vector_db:/data -v $(pwd)/$BACKUP_DIR:/backup \
  ubuntu tar xzf /backup/vector_db.tar.gz -C /data

# Restart services
docker-compose down
docker-compose up -d
```

### 6. Update Procedures

```bash
# Update services to latest version
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose down
docker-compose up -d

# Verify health
docker-compose ps
```

### 7. Security Hardening

**Recommended configurations:**

```yaml
# 1. Add authentication (api-gateway)
# 2. Enable HTTPS/TLS
# 3. Configure API rate limiting
# 4. Set resource limits per container
# 5. Configure network policies
# 6. Enable audit logging
# 7. Regular security scanning

deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### 8. Performance Monitoring

```bash
# Monitor resource usage
docker stats

# View logs with filtering
docker-compose logs --tail=100 api-gateway | grep ERROR

# Check service metrics
curl http://localhost:8000/metrics  # If Prometheus enabled
```

---

## Support and Resources

### Useful Commands

```bash
# View all running services
docker-compose ps -a

# View full logs for troubleshooting
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart specific service
docker-compose restart api-gateway

# Execute command in container
docker-compose exec api-gateway bash

# View service logs since specific time
docker-compose logs --since 2024-04-07T10:00:00

# Scale service (Docker Compose)
docker-compose up -d --scale extract-agent=3
```

### Documentation References

- **Architecture**: See `ARCHITECTURE.md`
- **API Documentation**: Available at `http://localhost:8000/docs` (Swagger UI)
- **Service Logs**: `docker-compose logs <service-name>`
- **Configuration**: `.env.example` and `docker-compose.yml`

### Getting Help

1. **Check logs first**: `docker-compose logs -f`
2. **Health checks**: Verify all services are healthy
3. **Port availability**: Ensure all required ports are free
4. **Memory**: Verify sufficient RAM is available
5. **Network**: Test Docker network connectivity

### Reporting Issues

Include the following information:

```bash
# System information
docker --version
docker-compose --version
uname -a  # OS info

# Service logs
docker-compose logs > logs.txt

# Configuration (without secrets)
cat .env | grep -v PASSWORD > config.txt

# Health status
docker-compose ps > status.txt
```

---

## Upgrade Path

### From Previous Versions

**Backup current installation:**
```bash
docker-compose down -v
cp .env .env.backup
```

**Install new version:**
```bash
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

**Verify:**
```bash
docker-compose ps
curl http://localhost:8000/health
```

---

## Conclusion

You now have a fully functional KYC/AML Agentic AI System running locally or in production. For detailed architectural information, see `ARCHITECTURE.md`.

---

**Document Information:**
- **Version**: 1.0
- **Created**: April 7, 2026
- **Last Updated**: April 7, 2026
- **Status**: Complete
- **Next Review**: Q3 2026

