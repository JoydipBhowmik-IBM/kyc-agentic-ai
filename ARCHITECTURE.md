# 🏗️ KYC Agentic AI - Architecture Documentation

## System Architecture Overview

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   KYC AGENTIC AI - SYSTEM ARCHITECTURE                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝


                              CLIENT LAYER
                                  │
                    ┌─────────────────────────────┐
                    │   Web Browser / Client      │
                    │  (http://localhost:3000)    │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    FRONTEND LAYER           │
                    │  (React + Node.js)          │
                    │  Port: 3000                 │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    API GATEWAY LAYER        │
                    │   (FastAPI)                 │
                    │   Port: 8000                │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  ORCHESTRATION SERVICE      │
                    │   (FastAPI)                 │
                    │   Port: 8010                │
                    └──────────────┬──────────────┘
                                   │
              ┌────────┬───────────┼───────────┬────────┐
              │        │           │           │        │
              ▼        ▼           ▼           ▼        ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
        │Extract  │ │ Verify  │ │ Reason  │ │  Risk   │ │Decision │
        │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │
        │(8001)   │ │ (8002)  │ │ (8003)  │ │ (8004)  │ │ (8005)  │
        │FastAPI  │ │ FastAPI │ │ FastAPI │ │ FastAPI │ │ FastAPI │
        └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
             │           │           │           │           │
             └───────────┼───────────┼───────────┼───────────┘
                         │
                    ┌────▼─────┐
                    │  OLLAMA   │
                    │   LLM     │
                    │ (11434)   │
                    └───────────┘

                    MICROSERVICES LAYER
                    (All in Docker containers)
```

---

## 📋 Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Overview](#component-overview)
3. [Data Flow](#data-flow)
4. [Communication Patterns](#communication-patterns)
5. [Service Dependencies](#service-dependencies)
6. [Technology Stack](#technology-stack)
7. [Deployment Architecture](#deployment-architecture)
8. [Security Architecture](#security-architecture)

---

## 🏛️ High-Level Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  React Web UI (Frontend)                               │ │
│  │  - User Interface                                      │ │
│  │  - Document Upload                                    │ │
│  │  - Results Display                                    │ │
│  │  Port: 3000 (Node.js)                                │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────────────┘
                     │ HTTP/REST
                     │
┌────────────────────▼───────────────────────────────────────┐
│                  API LAYER                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastAPI Gateway                                       │ │
│  │  - Request Routing                                     │ │
│  │  - Authentication                                     │ │
│  │  - Response Aggregation                               │ │
│  │  Port: 8000                                           │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────────────┘
                     │ HTTP/REST
                     │
┌────────────────────▼───────────────────────────────────────┐
│              ORCHESTRATION LAYER                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Orchestration Service                                 │ │
│  │  - Workflow Management                                 │ │
│  │  - Agent Orchestration                                 │ │
│  │  - Process Coordination                               │ │
│  │  Port: 8010                                           │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────────────┘
                     │ HTTP/REST
                     │
┌────────────────────▼───────────────────────────────────────┐
│             MICROSERVICES LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Extract    │  │   Verify     │  │   Reason     │     │
│  │   Agent      │  │   Agent      │  │   Agent      │     │
│  │   (8001)     │  │   (8002)     │  │   (8003)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │   Risk       │  │   Decision   │                       │
│  │   Agent      │  │   Agent      │                       │
│  │   (8004)     │  │   (8005)     │                       │
│  └──────────────┘  └──────────────┘                       │
│  ┌──────────────────────────────────┐                     │
│  │   Ollama LLM Service             │                     │
│  │   (11434)                        │                     │
│  └──────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                     │
                     │
┌────────────────────▼───────────────────────────────────────┐
│              DATA & STORAGE LAYER                           │
│  - Document Processing                                     │
│  - Temporary Storage                                       │
│  - Cache Management                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Overview

### 1. Frontend (Port 3000)

```
┌───────────────────────────────────────────┐
│         FRONTEND - React Application      │
├───────────────────────────────────────────┤
│                                           │
│  Technology: Node.js + React              │
│  Purpose: User Interface                  │
│                                           │
│  Features:                                │
│  ├─ Document Upload Interface             │
│  ├─ Drag & Drop Support                   │
│  ├─ Results Display                       │
│  ├─ Process Status Tracking               │
│  └─ Error Handling & Alerts               │
│                                           │
│  Port: 3000                              │
│  Protocol: HTTP/REST                      │
│  Server: Express.js                       │
│                                           │
└───────────────────────────────────────────┘
         │
         │ POST /process
         │ Sends: Document + Metadata
         ▼
    API Gateway (8000)
```

### 2. API Gateway (Port 8000)

```
┌───────────────────────────────────────────┐
│      API GATEWAY - FastAPI                │
├───────────────────────────────────────────┤
│                                           │
│  Technology: Python FastAPI               │
│  Purpose: Central API Entry Point         │
│                                           │
│  Functions:                               │
│  ├─ Route Requests                        │
│  ├─ Validate Input                        │
│  ├─ Load Balance                          │
│  ├─ Handle Errors                         │
│  └─ Aggregate Responses                   │
│                                           │
│  Endpoints:                               │
│  ├─ POST /process (document upload)      │
│  ├─ GET /status (check processing)       │
│  ├─ GET /health (health check)           │
│  └─ GET /results (get results)           │
│                                           │
│  Port: 8000                              │
│  Protocol: HTTP/REST                      │
│  Framework: FastAPI                       │
│                                           │
└───────────────────────────────────────────┘
         │
         │ Forwards to Orchestration
         ▼
   Orchestration (8010)
```

### 3. Orchestration Service (Port 8010)

```
┌────────────────────────────────────────────┐
│   ORCHESTRATION SERVICE - FastAPI          │
├────────────────────────────────────────────┤
│                                            │
│  Technology: Python FastAPI                │
│  Purpose: Workflow Orchestration           │
│                                            │
│  Responsibilities:                         │
│  ├─ Coordinate Agent Calls                │
│  ├─ Manage Workflow State                 │
│  ├─ Handle Parallel Processing            │
│  ├─ Manage Timeouts                       │
│  └─ Return Aggregated Results             │
│                                            │
│  KYC Workflow:                             │
│  1. Extract Text (Extract Agent)           │
│  2. Verify Document (Verify Agent)        │
│  3. Analyze Context (Reason Agent)        │
│  4. Assess Risk (Risk Agent)              │
│  5. Make Decision (Decision Agent)        │
│                                            │
│  Port: 8010                               │
│  Protocol: HTTP/REST                       │
│  Framework: FastAPI                        │
│                                            │
└────────────────────────────────────────────┘
         │
    ┌────┴────┬──────────┬──────────┬────────┐
    │          │          │          │        │
    ▼          ▼          ▼          ▼        ▼
  8001       8002       8003       8004     8005
 Extract    Verify     Reason      Risk    Decision
 Agent      Agent      Agent       Agent   Agent
```

### 4. Agent Services (Microservices)

```
┌──────────────────────────────────────────────────┐
│          MICROSERVICES LAYER                     │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │ 1. EXTRACT AGENT (Port 8001)            │    │
│  │    Purpose: Document Text Extraction    │    │
│  │    Tech: FastAPI + Tesseract OCR        │    │
│  │    Input: Document Image                │    │
│  │    Output: Extracted Text               │    │
│  │                                         │    │
│  │ 2. VERIFY AGENT (Port 8002)             │    │
│  │    Purpose: Document Verification       │    │
│  │    Tech: FastAPI + Validation Rules     │    │
│  │    Input: Extracted Text                │    │
│  │    Output: Verification Result          │    │
│  │                                         │    │
│  │ 3. REASON AGENT (Port 8003)             │    │
│  │    Purpose: Reasoning & Analysis        │    │
│  │    Tech: FastAPI + LLM Integration      │    │
│  │    Input: Document Data                 │    │
│  │    Output: Analysis Results             │    │
│  │                                         │    │
│  │ 4. RISK AGENT (Port 8004)               │    │
│  │    Purpose: Risk Assessment             │    │
│  │    Tech: FastAPI + Risk Models          │    │
│  │    Input: Document Analysis             │    │
│  │    Output: Risk Score                   │    │
│  │                                         │    │
│  │ 5. DECISION AGENT (Port 8005)           │    │
│  │    Purpose: Final Decision Making       │    │
│  │    Tech: FastAPI + Decision Logic       │    │
│  │    Input: Risk Score + Analysis         │    │
│  │    Output: APPROVE/REJECT               │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │ OLLAMA LLM SERVICE (Port 11434)          │    │
│  │ Purpose: Language Model Inference        │    │
│  │ Tech: Ollama Container                   │    │
│  │ Models: Local LLM Models                 │    │
│  │ Used by: Reason, Risk, Decision Agents   │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│     ALL SERVICES RUN IN DOCKER CONTAINERS        │
│     Total: 9 Containers (8 services + orchestration)
└──────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

### KYC Document Processing Flow

```
┌────────────────────────────────────────────────────────────────┐
│ START: User uploads KYC Document                              │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼ (HTTP POST)
    ┌──────────────────┐
    │  Frontend (3000) │
    │  Upload Form     │
    └────────┬─────────┘
             │
             ▼ (HTTP POST /process)
    ┌──────────────────┐
    │ API Gateway      │
    │ (8000)           │
    │ Validate Input   │
    └────────┬─────────┘
             │
             ▼ (HTTP POST /orchestrate)
    ┌──────────────────────────────────┐
    │ Orchestration Service (8010)    │
    │ Create Processing Pipeline      │
    └────────┬───────────────────────┘
             │
    ┌────────┴────┬──────────┬──────────┬────────┐
    │             │          │          │        │
    ▼             ▼          ▼          ▼        ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│Extract │  │        │  │        │  │        │  │        │
│ (8001) │  │        │  │        │  │        │  │        │
│        │  │        │  │        │  │        │  │        │
│Extract │  │        │  │        │  │        │  │        │
│ Text   │  │        │  │        │  │        │  │        │
│        │  │        │  │        │  │        │  │        │
│        ▼  │        │  │        │  │        │  │        │
│ Output:   │        │  │        │  │        │  │        │
│ Raw Text  │        │  │        │  │        │  │        │
└────────┘  │        │  │        │  │        │  │        │
    │       │        │  │        │  │        │  │        │
    ▼       ▼        │  │        │  │        │  │        │
    │   ┌────────┐   │  │        │  │        │  │        │
    │   │ Verify │   │  │        │  │        │  │        │
    │   │ (8002) │   │  │        │  │        │  │        │
    │   │        │   │  │        │  │        │  │        │
    │   │ Verify │   │  │        │  │        │  │        │
    │   │ Format │   │  │        │  │        │  │        │
    │   │        │   │  │        │  │        │  │        │
    │   │        ▼   │  │        │  │        │  │        │
    │   │ Output:    │  │        │  │        │  │        │
    │   │ Verified   │  │        │  │        │  │        │
    │   └────────┘   │  │        │  │        │  │        │
    │       │        │  │        │  │        │  │        │
    │       ▼        ▼  │        │  │        │  │        │
    │       │    ┌────────┐      │  │        │  │        │
    │       │    │ Reason │      │  │        │  │        │
    │       │    │ (8003) │      │  │        │  │        │
    │       │    │        │      │  │        │  │        │
    │       │    │ Analyze│ (Uses Ollama)    │  │        │
    │       │    │        │      │  │        │  │        │
    │       │    │        ▼      │  │        │  │        │
    │       │    │ Output:       │  │        │  │        │
    │       │    │ Analysis      │  │        │  │        │
    │       │    └────────┘      │  │        │  │        │
    │       │        │           │  │        │  │        │
    │       │        ▼           ▼  │        │  │        │
    │       │        │       ┌────────┐     │  │        │
    │       │        │       │ Risk   │     │  │        │
    │       │        │       │ (8004) │     │  │        │
    │       │        │       │        │     │  │        │
    │       │        │       │ Assess │(Uses Ollama)     │
    │       │        │       │ Risk   │     │  │        │
    │       │        │       │        │     │  │        │
    │       │        │       │        ▼     │  │        │
    │       │        │       │ Output:      │  │        │
    │       │        │       │ Risk Score   │  │        │
    │       │        │       └────────┘     │  │        │
    │       │        │           │          │  │        │
    │       │        │           ▼          ▼  │        │
    │       │        │           │      ┌────────┐      │
    │       │        │           │      │Decision│      │
    │       │        │           │      │ (8005) │      │
    │       │        │           │      │        │      │
    │       │        │           │      │ Decide │      │
    │       │        │           │      │        │      │
    │       │        │           │      │        ▼      │
    │       │        │           │      │ Output:       │
    │       │        │           │      │ APPROVE/REJECT
    │       │        │           │      └────────┘      │
    └───────┴────────┴───────────┴──────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Send Results to      │
                    │ Frontend (8000)      │
                    └────────┬─────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │ Display Results      │
                    │ User sees Decision   │
                    │ and Details          │
                    └────────┬─────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │ END: Process         │
                    │ Complete             │
                    └──────────────────────┘
```

---

## 🔄 Communication Patterns

### Synchronous Request-Response

```
Frontend (3000)
    │
    │ POST /process
    │ {"document": "base64_data"}
    │────────────────────────────────────────►
                                             API Gateway (8000)
                                             │
                                             │ POST /orchestrate
                                             │──────────────────────────►
                                                     Orchestration (8010)
                                                     │
                                                     ├─► Extract (8001)
                                                     │   Wait for response
                                                     │
                                                     ├─► Verify (8002)
                                                     │   Wait for response
                                                     │
                                                     └─► Others...
                                                     │
                                         Response ◄──┘
                                         │
                                    Response ◄──
                                             │
Results Displayed ◄──────────────────────────┘
```

### Data Transfer Format

```
REQUEST:
┌──────────────────────────────────┐
│ HTTP POST /process               │
│ Content-Type: application/json   │
│                                  │
│ {                                │
│   "document": "base64_string",   │
│   "document_type": "KYC",        │
│   "client_id": "123",            │
│   "metadata": {...}              │
│ }                                │
└──────────────────────────────────┘

RESPONSE:
┌──────────────────────────────────┐
│ HTTP 200 OK                      │
│ Content-Type: application/json   │
│                                  │
│ {                                │
│   "status": "success",           │
│   "document_type": "Aadhar",     │
│   "confidence": 0.95,            │
│   "decision": "APPROVED",        │
│   "risk_score": 0.2,             │
│   "processing_time": 1.5,        │
│   "details": {...}               │
│ }                                │
└──────────────────────────────────┘
```

---

## 🔗 Service Dependencies

### Dependency Graph

```
                    Frontend (3000)
                          │
                          ▼
                   API Gateway (8000)
                          │
                          ▼
              Orchestration Service (8010)
                          │
              ┌─────────┬─┼─┬────────┬──────┐
              │         │ │ │        │      │
              ▼         ▼ ▼ ▼        ▼      ▼
           Extract  Verify Reason  Risk   Decision
           (8001)   (8002) (8003)  (8004) (8005)
              │         │     │       │      │
              │         │     └─────┬─┘      │
              │         │           │       │
              └─────────┴─────┬─────┴───────┘
                              │
                              ▼
                        Ollama LLM (11434)
                        (Shared Service)

LEGEND:
─────────────────
→ Direct Call
  ─ Shared Dependency
```

### Startup Order

```
1. Start Ollama First (Port 11434)
   └─ Required by: Reason, Risk, Decision Agents

2. Start Individual Agents (Ports 8001-8005)
   └─ Extract, Verify, Reason, Risk, Decision

3. Start Orchestration (Port 8010)
   └─ Depends on: Agents

4. Start API Gateway (Port 8000)
   └─ Depends on: Orchestration

5. Start Frontend (Port 3000)
   └─ Depends on: API Gateway

All managed by Docker Compose!
```

---

## 💻 Technology Stack

### Backend Services

```
┌─────────────────────────────────────────┐
│         TECHNOLOGY STACK                │
├─────────────────────────────────────────┤
│                                         │
│ LANGUAGE & RUNTIME:                     │
│ • Python 3.10+                          │
│ • Node.js 16+                           │
│                                         │
│ WEB FRAMEWORKS:                         │
│ • FastAPI (Python - API Services)       │
│ • Express.js (Node.js - Frontend)       │
│                                         │
│ ASYNC/CONCURRENCY:                      │
│ • asyncio (Python)                      │
│ • uvicorn (ASGI server)                 │
│                                         │
│ OCR & TEXT PROCESSING:                  │
│ • Tesseract OCR                         │
│ • PIL/Pillow (Image Processing)         │
│ • pytesseract (Tesseract Wrapper)       │
│                                         │
│ LLM & AI:                               │
│ • Ollama (LLM Runtime)                  │
│ • LLaMA/Mistral Models                  │
│                                         │
│ FRONTEND:                               │
│ • React.js                              │
│ • HTML/CSS/JavaScript                   │
│                                         │
│ CONTAINERIZATION:                       │
│ • Docker                                │
│ • Docker Compose                        │
│                                         │
│ LIBRARIES:                              │
│ • requests (HTTP Client)                │
│ • numpy/pandas (Data Processing)        │
│ • scikit-learn (ML Models)              │
│ • pydantic (Data Validation)            │
│                                         │
└─────────────────────────────────────────┘
```

### Dependencies by Service

```
Extract Agent (8001):
  ├─ FastAPI
  ├─ Tesseract OCR
  ├─ PIL/Pillow
  ├─ pytesseract
  └─ pydantic

Verify Agent (8002):
  ├─ FastAPI
  ├─ pydantic
  └─ validation libraries

Reason Agent (8003):
  ├─ FastAPI
  ├─ Ollama Client
  ├─ LLM Integration
  └─ pydantic

Risk Agent (8004):
  ├─ FastAPI
  ├─ Ollama Client
  ├─ Scikit-learn
  ├─ numpy
  └─ pydantic

Decision Agent (8005):
  ├─ FastAPI
  ├─ Ollama Client
  ├─ Decision Logic
  └─ pydantic

Orchestration (8010):
  ├─ FastAPI
  ├─ HTTP Client
  ├─ asyncio
  └─ pydantic

API Gateway (8000):
  ├─ FastAPI
  ├─ HTTP Client
  └─ pydantic

Frontend (3000):
  ├─ React
  ├─ Axios/Fetch
  ├─ CSS Frameworks
  └─ UI Libraries

Ollama (11434):
  ├─ Go Runtime
  ├─ LLaMA/Mistral Models
  └─ Vector Processing
```

---

## 🐳 Deployment Architecture

### Docker Container Structure

```
┌─────────────────────────────────────────────────────────┐
│           DOCKER COMPOSE CONFIGURATION                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Version: 3.8                                           │
│  Network: kyc-network (bridge)                          │
│                                                         │
│  Services:                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-frontend                                     │   │
│  │ ├─ Image: node:16-slim                          │   │
│  │ ├─ Container: kyc-frontend                      │   │
│  │ ├─ Ports: 3000:3000                             │   │
│  │ ├─ Env: NODE_ENV=production                     │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-api-gateway                                 │   │
│  │ ├─ Image: kyc-agentic-ai-api-gateway            │   │
│  │ ├─ Container: kyc-api-gateway                   │   │
│  │ ├─ Ports: 8000:8000                             │   │
│  │ ├─ Env: PYTHONUNBUFFERED=1                      │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-orchestration-service                       │   │
│  │ ├─ Image: kyc-agentic-ai-orchestration-service │   │
│  │ ├─ Container: kyc-orchestration-service         │   │
│  │ ├─ Ports: 8010:8010                             │   │
│  │ ├─ Env: PYTHONUNBUFFERED=1                      │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-extract-agent                               │   │
│  │ ├─ Image: kyc-agentic-ai-extract-agent          │   │
│  │ ├─ Container: kyc-extract-agent                 │   │
│  │ ├─ Ports: 8001:8000                             │   │
│  │ ├─ Volumes: /usr/share/tesseract-ocr            │   │
│  │ ├─ Env: PYTHONUNBUFFERED=1                      │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-verify-agent                                │   │
│  │ ├─ Image: kyc-agentic-ai-verify-agent           │   │
│  │ ├─ Container: kyc-verify-agent                  │   │
│  │ ├─ Ports: 8002:8000                             │   │
│  │ ├─ Env: PYTHONUNBUFFERED=1                      │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-reason-agent                                │   │
│  │ ├─ Image: kyc-agentic-ai-reason-agent           │   │
│  │ ├─ Container: kyc-reason-agent                  │   │
│  │ ├─ Ports: 8003:8000                             │   │
│  │ ├─ Env: PYTHONUNBUFFERED=1                      │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-risk-agent                                  │   │
│  │ ├─ Image: kyc-agentic-ai-risk-agent             │   │
│  │ ├─ Container: kyc-risk-agent                    │   │
│  │ ├─ Ports: 8004:8000                             │   │
│  │ ├─ Env: PYTHONUNBUFFERED=1                      │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-decision-agent                              │   │
│  │ ├─ Image: kyc-agentic-ai-decision-agent         │   │
│  │ ├─ Container: kyc-decision-agent                │   │
│  │ ├─ Ports: 8005:8000                             │   │
│  │ ├─ Env: PYTHONUNBUFFERED=1                      │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ kyc-ollama                                      │   │
│  │ ├─ Image: ollama/ollama:latest                  │   │
│  │ ├─ Container: kyc-ollama                        │   │
│  │ ├─ Ports: 11434:11434                           │   │
│  │ ├─ Volumes: /root/.ollama                       │   │
│  │ └─ Health Check: ✓                              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Network: kyc-network (all containers connected)       │
│  Volume Management: Docker volumes for persistence     │
│  Restart Policy: always                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔒 Security Architecture

### Network Security

```
┌─────────────────────────────────────────┐
│     SECURITY ARCHITECTURE               │
├─────────────────────────────────────────┤
│                                         │
│ NETWORK LAYER:                          │
│ • Docker Bridge Network (kyc-network)   │
│ • Isolated Container Communication      │
│ • No Direct Internet Access (Optional)  │
│                                         │
│ API LAYER:                              │
│ • CORS Configuration                    │
│ • Request Validation                    │
│ • Rate Limiting (Optional)              │
│ • Input Sanitization                    │
│                                         │
│ DATA LAYER:                             │
│ • Document Encryption (Optional)        │
│ • Secure File Storage                   │
│ • Temporary File Cleanup                │
│                                         │
│ ACCESS CONTROL:                         │
│ • Container Isolation                   │
│ • Port Exposure Control                 │
│ • Environment Variable Security         │
│                                         │
│ MONITORING:                             │
│ • Health Checks per Service             │
│ • Log Aggregation                       │
│ • Error Tracking                        │
│                                         │
└─────────────────────────────────────────┘
```

### Data Flow Security

```
Client Input
    │
    ▼ (VALIDATE)
┌─────────────────┐
│ Input Validation│
│ • Type Check    │
│ • Size Check    │
│ • Format Check  │
└────────┬────────┘
         │ (SANITIZE)
         ▼
┌─────────────────┐
│ Sanitization    │
│ • Remove Inject │
│ • Clean Paths   │
│ • Verify Origin │
└────────┬────────┘
         │ (PROCESS)
         ▼
┌─────────────────┐
│ Process in Agent│
│ • Isolated      │
│ • Containerized │
│ • Limited Access│
└────────┬────────┘
         │ (SECURE)
         ▼
┌─────────────────┐
│ Return Response │
│ • Sanitized     │
│ • Validated     │
│ • Secure        │
└────────┬────────┘
         │
         ▼
Client Response
```

---

## 📈 Scaling & Performance

### Horizontal Scaling

```
┌──────────────────────────────────────────┐
│    CURRENT ARCHITECTURE (Single Host)    │
│                                          │
│  Frontend ── Gateway ── Orchestration    │
│                            │             │
│              ┌─────────────┼─────────┐   │
│              ▼             ▼         ▼   │
│          Agents (5)    Ollama (1)       │
│                                          │
│  Single Docker Compose Setup             │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│    SCALABLE ARCHITECTURE (Multi-Host)    │
│                                          │
│  Load Balancer                           │
│     │                                    │
│     ├─► Frontend Cluster                │
│     ├─► API Gateway Cluster             │
│     ├─► Orchestration Cluster           │
│     └─► Agent Cluster                   │
│          │                              │
│          ├─► Extract (3 instances)      │
│          ├─► Verify (2 instances)       │
│          └─► Decision (2 instances)     │
│                                          │
│  Shared: Ollama LLM Service              │
│                                          │
│  Orchestration: Kubernetes               │
└──────────────────────────────────────────┘
```

---

## 📊 Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│           ARCHITECTURE SUMMARY TABLE                     │
├─────────────────────────────────────────────────────────┤
│ Layer          │ Component        │ Technology          │
├────────────────┼──────────────────┼─────────────────────┤
│ Presentation   │ Frontend         │ React + Express    │
│ API            │ Gateway          │ FastAPI            │
│ Orchestration  │ Coordinator      │ FastAPI            │
│ Microservices  │ Extract          │ FastAPI + Tesseract│
│                │ Verify           │ FastAPI            │
│                │ Reason           │ FastAPI + LLM      │
│                │ Risk             │ FastAPI + LLM      │
│                │ Decision         │ FastAPI + LLM      │
│ AI/ML          │ LLM Service      │ Ollama             │
│ Container      │ Orchestration    │ Docker Compose     │
│ Deployment     │ Infrastructure   │ Docker Containers  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Architectural Principles

```
1. MICROSERVICES PATTERN
   ✓ Each service: Single responsibility
   ✓ Independent deployment
   ✓ Technology flexibility

2. API-FIRST DESIGN
   ✓ RESTful APIs
   ✓ Standard JSON format
   ✓ Clear contracts

3. CONTAINERIZATION
   ✓ Consistent environments
   ✓ Easy deployment
   ✓ Simplified scaling

4. ORCHESTRATION
   ✓ Centralized workflow
   ✓ Error handling
   ✓ Result aggregation

5. SCALABILITY
   ✓ Stateless services
   ✓ Horizontal scaling
   ✓ Load balancing

6. RELIABILITY
   ✓ Health checks
   ✓ Graceful degradation
   ✓ Error recovery
```

---

**Architecture Documentation Version:** 1.0  
**Last Updated:** March 23, 2026  
**Status:** ✅ Production Ready

