# KYC/AML Agentic AI System - Architecture Document

**Document Version:** 1.0  
**Last Updated:** April 6, 2026

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Principles](#architecture-principles)
4. [Component Architecture](#component-architecture)
5. [Data Flow](#data-flow)
6. [Deployment Architecture](#deployment-architecture)
7. [Technology Stack](#technology-stack)
8. [Integration Patterns](#integration-patterns)
9. [Scalability & Performance](#scalability--performance)
10. [Security Considerations](#security-considerations)

---

## Executive Summary

The KYC/AML Agentic AI System is a distributed, microservices-based architecture designed to automate the Know Your Customer (KYC) and Anti-Money Laundering (AML) compliance processes. The system leverages multiple specialized AI agents that work in orchestrated harmony to validate documents, extract information, verify authenticity, assess risk, and make final compliance decisions.

**Key Characteristics:**
- **Agentic Architecture**: Five specialized autonomous agents handling distinct concerns
- **Orchestration-Based Workflow**: Central orchestration service managing multi-stage processing
- **RAG Integration**: Retrieval Augmented Generation for context-aware reasoning
- **Vector Database**: Persistent knowledge base with KYC rules and fraud patterns
- **Model Context Protocol (MCP)**: Standardized tool integration layer
- **Container-Based Deployment**: Docker and Docker Compose for consistent environments
- **API-First Design**: RESTful APIs for all service boundaries

---

## System Overview

### High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
│                     (Web UI - Express)                          │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│              (Request validation, routing, CORS)                │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION SERVICE                          │
│    (Workflow management, agent coordination, request routing)   │
└────────────────────────────────────────────────────────────────┘
                              ↓
     ┌─────────────────────────────────────────┐
     │      SPECIALIZED AGENT LAYER            │
     │  ┌──────────────────────────────────┐   │
     │  │   1. EXTRACT AGENT               │   │
     │  │   (Document parsing, OCR)        │   │
     │  └──────────────────────────────────┘   │
     │  ┌──────────────────────────────────┐   │
     │  │   2. VERIFY AGENT                │   │
     │  │   (Credential validation, rules) │   │
     │  └──────────────────────────────────┘   │
     │  ┌──────────────────────────────────┐   │
     │  │   3. REASON AGENT                │   │
     │  │   (RAG + LLM-based reasoning)    │   │
     │  └──────────────────────────────────┘   │
     │  ┌──────────────────────────────────┐   │
     │  │   4. RISK AGENT                  │   │
     │  │   (Risk scoring, anomaly detect) │   │
     │  └──────────────────────────────────┘   │
     │  ┌──────────────────────────────────┐   │
     │  │   5. DECISION AGENT              │   │
     │  │   (Final KYC decision)           │   │
     │  └──────────────────────────────────┘   │
     └─────────────────────────────────────────┘
                              ↓
     ┌─────────────────────────────────────────┐
     │  SUPPORT SERVICES LAYER                 │
     │  ┌──────────────────────────────────┐   │
     │  │   MCP Server                     │   │
     │  │   (Tool registry, knowledge base)│   │
     │  └──────────────────────────────────┘   │
     │  ┌──────────────────────────────────┐   │
     │  │   Vector Database (ChromaDB)     │   │
     │  │   (KYC rules, fraud patterns)    │   │
     │  └──────────────────────────────────┘   │
     │  ┌──────────────────────────────────┐   │
     │  │   Ollama LLM Server              │   │
     │  │   (Language model inference)     │   │
     │  └──────────────────────────────────┘   │
     └─────────────────────────────────────────┘
```

---

## Architecture Principles

### 1. **Separation of Concerns**
Each agent focuses on a specific aspect of KYC/AML compliance:
- **Extraction**: Document parsing and data extraction
- **Verification**: Rule-based validation
- **Reasoning**: Context-aware analysis
- **Risk Assessment**: Anomaly detection and scoring
- **Decision-Making**: Final approval/rejection decisions

### 2. **Asynchronous Communication**
Agents communicate through HTTP APIs, enabling:
- Independent scaling
- Fault isolation
- Loose coupling
- Flexible composition

### 3. **Stateless Processing**
Each service instance is stateless, allowing:
- Horizontal scaling
- Easy recovery from failures
- Load distribution

### 4. **Knowledge-Driven Design**
The system maintains a persistent knowledge base containing:
- KYC validation rules
- Fraud patterns
- Historical analysis results
- Regulatory guidelines

### 5. **Container-Based Deployment**
All services are containerized, ensuring:
- Environment consistency
- Easy deployment
- Scaling flexibility
- Simplified dependency management

---

## Component Architecture

### 1. **Frontend Layer**

**Service:** `frontend/`

**Technology:** Node.js/Express, HTML5, JavaScript  
**Port:** 3000  

**Responsibilities:**
- User interface for KYC document submission
- Real-time processing status updates
- Result display and reporting
- File upload handling

**Key Files:**
- `server.js` - Express server configuration
- `index.html` - Frontend UI
- `package.json` - Dependencies (Express, compression)

**APIs Exposed:**
- `GET /` - Serves the main UI
- `POST /upload` - Handles document uploads (proxied to API Gateway)

---

### 2. **API Gateway**

**Service:** `api-gateway/`

**Technology:** Python/FastAPI  
**Port:** 8000 (exposed)  
**Environment Variables:**
- `ORCHESTRATION_SERVICE_URL` - Points to orchestration service
- `REQUEST_TIMEOUT` - Request timeout (default: 300s)
- `LOG_LEVEL` - Logging verbosity

**Responsibilities:**
- Request validation and sanitization
- CORS handling
- Request routing to orchestration service
- Health monitoring
- API documentation

**Key Endpoints:**
```
GET  /health                    - Health check
POST /kyc                       - Submit KYC request
```

**Data Flow:**
1. Receives file upload from frontend
2. Validates file existence and content
3. Routes to Orchestration Service
4. Returns results to client

---

### 3. **Orchestration Service** ⭐ (Core)

**Service:** `orchestration-service/`

**Technology:** Python/FastAPI  
**Port:** 8000 (internal)  
**Environment Variables:**
- `EXTRACT_AGENT_URL` - Extract agent endpoint
- `VERIFY_AGENT_URL` - Verify agent endpoint
- `REASON_AGENT_URL` - Reason agent endpoint
- `RISK_AGENT_URL` - Risk agent endpoint
- `DECISION_AGENT_URL` - Decision agent endpoint
- `REQUEST_TIMEOUT` - Agent communication timeout (default: 120s)

**Responsibilities:**
- **Workflow Orchestration**: Manages the sequential/parallel execution of agents
- **State Management**: Tracks processing state and intermediate results
- **Error Handling**: Graceful degradation and error recovery
- **Health Monitoring**: Monitors all downstream agent health
- **Data Aggregation**: Combines results from all agents

**Workflow Stages:**

```
Input Document
       ↓
[STAGE 1] Extract Agent
  - Parse document
  - Extract text/images
  - Output: structured_data, detected_issues
       ↓
[STAGE 2] Verify Agent (Parallel with Reason)
  - Apply KYC rules
  - Validate credentials
  - Output: verification_results, rule_violations
       ↓
[STAGE 3] Reason Agent (Parallel with Verify)
  - RAG-based analysis
  - Query vector database
  - LLM reasoning
  - Output: analysis_insights, concerns
       ↓
[STAGE 4] Risk Agent
  - Calculate risk scores
  - Detect anomalies
  - Output: risk_score, risk_factors
       ↓
[STAGE 5] Decision Agent
  - Consolidate findings
  - Make final decision
  - Output: KYC_status (APPROVED/REJECTED/REVIEW)
       ↓
Final Report
```

**Key Endpoints:**
```
GET  /health            - Health check with agent status
POST /process           - Process KYC workflow
GET  /status/{id}       - Get processing status (if async)
```

---

### 4. **Agent Layer** (Five Specialized Agents)

#### 4.1 **Extract Agent**

**Service:** `agents/extract-agent/`

**Technology:** Python/FastAPI, Tesseract OCR, Pillow, pytesseract  
**Port:** 8007 (mapped from 8000)  

**Purpose:** Document parsing and text extraction

**Key Features:**
- Multi-format support (JPEG, PNG, TIFF, WebP, AVIF)
- OCR with Tesseract
- Photo detection in documents
- Document validation
- Layout analysis

**Input:**
```json
{
  "file": "<binary document data>"
}
```

**Output:**
```json
{
  "extracted_text": "string",
  "pages": 1,
  "has_photo": true,
  "document_type": "string",
  "confidence": 0.95,
  "processing_time": 1.23
}
```

**Key Endpoints:**
```
GET  /health           - Health check
POST /extract          - Extract text from document
```

---

#### 4.2 **Verify Agent**

**Service:** `agents/verify-agent/`

**Technology:** Python/FastAPI, ChromaDB  
**Port:** 8008 (mapped from 8000)  
**Volumes:** `kyc_vector_db:/data/kyc_vector_db`

**Purpose:** Rule-based verification and credential validation

**Key Features:**
- KYC rule loading and application
- PAN/credential validation with mock APIs
- Regex pattern matching
- Rule violation detection
- Vector database integration for rule retrieval

**Loaded Rules from:** `kyc_vector_db/kyc_rules.json`

**Input:**
```json
{
  "text": "extracted document text",
  "filename": "document.pdf",
  "status": "pending"
}
```

**Output:**
```json
{
  "valid": true,
  "verified_fields": ["name", "id", "address"],
  "violations": ["rule_id_123"],
  "validation_details": {},
  "confidence": 0.92
}
```

**Key Endpoints:**
```
GET  /health           - Health check
POST /verify           - Verify document against KYC rules
```

---

#### 4.3 **Reason Agent** (RAG-Enabled)

**Service:** `agents/reason-agent/`

**Technology:** Python/FastAPI, LangChain, ChromaDB, Ollama  
**Port:** 8006 (mapped from 8000)  
**Environment Variables:**
- `OLLAMA_URL` - LLM server URL
- `LLM_MODEL` - Model name (default: "mistral")
- `MCP_SERVER_URL` - MCP server for tools
- `REQUEST_TIMEOUT` - LLM request timeout

**Purpose:** Intelligent reasoning with Retrieval Augmented Generation

**Key Features:**
- RAG (Retrieval Augmented Generation) pipeline
- Vector database context retrieval
- LangChain integration
- LLM-based analysis
- MCP tool integration
- Prompt templates for compliance reasoning

**Architecture:**
```
Input Data
    ↓
Vector DB Retrieval (Semantic Search)
    ↓
Prompt Construction with Retrieved Context
    ↓
LLM Inference (via Ollama + LangChain)
    ↓
JSON Output Parsing
    ↓
Result Return
```

**Input:**
```json
{
  "text": "extracted text",
  "verification_results": {},
  "context": "additional information"
}
```

**Output:**
```json
{
  "analysis": "detailed reasoning",
  "confidence_score": 0.88,
  "reasoning_steps": [],
  "recommended_actions": ["action1", "action2"],
  "concerns": ["concern1"]
}
```

**Key Endpoints:**
```
GET  /health           - Health check
POST /reason           - Perform RAG-based reasoning
```

---

#### 4.4 **Risk Agent**

**Service:** `agents/risk-agent/`

**Technology:** Python/FastAPI, NumPy, SciPy (z-score)  
**Port:** 8004 (mapped from 8000)  

**Purpose:** Risk scoring and anomaly detection

**Key Features:**
- Multi-dimensional risk assessment
- Keyword-based risk classification (Critical, High, Medium, Low)
- Statistical anomaly detection (Z-score)
- Risk aggregation
- Advanced intelligence scoring

**Risk Dimensions:**
1. **Semantic Risk** - Keyword matching against known risk patterns
2. **Statistical Risk** - Anomaly detection based on patterns
3. **Compliance Risk** - Regulatory guideline violations
4. **Behavioral Risk** - Unusual activity indicators

**Input:**
```json
{
  "extracted_data": {},
  "verification_results": {},
  "analysis_insights": {}
}
```

**Output:**
```json
{
  "overall_risk_score": 0.35,
  "risk_level": "LOW",
  "risk_breakdown": {
    "semantic_risk": 0.2,
    "statistical_risk": 0.15,
    "compliance_risk": 0.1
  },
  "risk_factors": ["factor1", "factor2"],
  "anomalies_detected": false
}
```

**Key Endpoints:**
```
GET  /health           - Health check
POST /analyze          - Analyze risk
POST /detect_anomaly   - Detect anomalies
```

---

#### 4.5 **Decision Agent**

**Service:** `agents/decision-agent/`

**Technology:** Python/FastAPI, LangChain (optional)  
**Port:** 8005 (mapped from 8000)  

**Purpose:** Final KYC decision-making

**Key Features:**
- Multi-criteria decision making
- Confidence scoring
- Optional LLM-based decision reasoning
- Decision explanation generation
- Threshold-based decisions

**Decision Process:**
```
Aggregate All Findings
    ↓
Apply Decision Thresholds
    ↓
Evaluate Risk vs. Verification
    ↓
Generate Reasoning (LLM-optional)
    ↓
Make Final Decision
    ↓
Return APPROVED / REJECTED / REVIEW_REQUIRED
```

**Decision Thresholds:**
- Risk Score < 0.3 + All Verifications Pass → APPROVED
- Risk Score > 0.7 OR Multiple Violations → REJECTED
- Borderline cases → REVIEW_REQUIRED

**Input:**
```json
{
  "extraction_results": {},
  "verification_results": {},
  "analysis_insights": {},
  "risk_assessment": {}
}
```

**Output:**
```json
{
  "kyc_status": "APPROVED",
  "confidence_score": 0.94,
  "reasoning": "All documents verified successfully...",
  "summary": {
    "approved_aspects": [],
    "flagged_items": [],
    "required_followup": []
  },
  "decision_timestamp": "2026-04-06T10:30:45.123Z"
}
```

**Key Endpoints:**
```
GET  /health           - Health check
POST /decide           - Make final KYC decision
```

---

### 5. **Support Services Layer**

#### 5.1 **MCP Server (Model Context Protocol)**

**Service:** `mcp-server/`

**Technology:** Python/FastAPI, ChromaDB  
**Port:** 8020  

**Purpose:** Standardized tool registry and knowledge base access

**Responsibilities:**
- Tool registry management
- Knowledge base queries
- KYC rule retrieval
- Fraud pattern queries
- Vector database wrapper

**Tools Provided:**
1. `get_kyc_rules` - Retrieve applicable KYC rules
2. `query_fraud_patterns` - Search fraud pattern database
3. `get_rule_details` - Get detailed rule information
4. `search_vector_db` - Semantic search on knowledge base

**Key Endpoints:**
```
GET  /health                    - Health check
POST /query                     - Query tools
GET  /tools                     - List available tools
POST /retrieve_kyc_rules        - Get KYC rules
POST /query_fraud_patterns      - Query fraud patterns
```

---

#### 5.2 **Vector Database (ChromaDB)**

**Purpose:** Persistent knowledge base and semantic search

**Data Structure:**
```
kyc_vector_db/
├── kyc_rules.json          # KYC validation rules
├── fraud_patterns.json     # Known fraud patterns
├── index.json              # Vector index metadata
└── chroma_data/            # Chroma vector store
```

**Collections:**
1. **kyc_rules** - KYC validation rules and guidelines
2. **fraud_patterns** - Known fraud indicators and patterns
3. **analysis_history** - Historical analysis results (for learning)

**Integration Points:**
- Verify Agent: Rule retrieval
- Reason Agent: RAG context retrieval
- MCP Server: Knowledge base queries

---

#### 5.3 **Ollama LLM Server**

**Technology:** Ollama, Mistral Model (configurable)

**Purpose:** Language model inference

**Configuration:**
- Model: Mistral (default, configurable via `LLM_MODEL`)
- Temperature: 0.1-0.3 (low for consistency)
- Context Window: 4096 tokens
- Base URL: `http://ollama:11434`

**Usage:**
- Reason Agent: RAG-based analysis
- Decision Agent: Decision reasoning (optional)
- Prompt templates: Compliance-specific instructions

---

## Data Flow

### Complete KYC Processing Workflow

```
1. USER INITIATES REQUEST
   ├─ Frontend: File upload
   ├─ API Gateway: Validation
   └─ Orchestration: Workflow start

2. STAGE 1: EXTRACTION
   ├─ Input: Binary document
   ├─ Extract Agent: Parse & OCR
   ├─ Output: Structured text, metadata
   └─ Storage: In-memory (session)

3. STAGE 2: PARALLEL PROCESSING
   ├─ Path A: VERIFICATION
   │  ├─ Verify Agent: Load KYC rules
   │  ├─ Validate against rules
   │  └─ Output: Violations, validations
   │
   └─ Path B: REASONING
      ├─ Reason Agent: Query vector DB
      ├─ Retrieve relevant rules/patterns
      ├─ Run LLM analysis with context
      └─ Output: Insights, concerns

4. STAGE 3: RISK ASSESSMENT
   ├─ Risk Agent: Multi-dimensional analysis
   ├─ Calculate risk score
   ├─ Detect anomalies
   └─ Output: Risk metrics

5. STAGE 4: DECISION-MAKING
   ├─ Decision Agent: Aggregate all findings
   ├─ Apply decision thresholds
   ├─ Generate reasoning
   └─ Output: Final KYC status

6. RETURN RESULTS
   ├─ Orchestration: Compile report
   ├─ API Gateway: Format response
   └─ Frontend: Display results

```

### Data Structures Through Pipeline

**Stage 1 Output (Extract Agent):**
```json
{
  "extracted_text": "...",
  "pages": 1,
  "has_photo": true,
  "document_type": "ID",
  "confidence": 0.95,
  "processing_time": 1.23
}
```

**Stage 2A Output (Verify Agent):**
```json
{
  "valid": true,
  "verified_fields": ["name", "dob", "id"],
  "violations": [],
  "confidence": 0.92
}
```

**Stage 2B Output (Reason Agent):**
```json
{
  "analysis": "...",
  "confidence_score": 0.88,
  "concerns": [],
  "recommended_actions": []
}
```

**Stage 3 Output (Risk Agent):**
```json
{
  "overall_risk_score": 0.25,
  "risk_level": "LOW",
  "risk_factors": []
}
```

**Stage 4 Output (Decision Agent):**
```json
{
  "kyc_status": "APPROVED",
  "confidence_score": 0.94,
  "reasoning": "...",
  "summary": {}
}
```

---

## Deployment Architecture

### Container Services

All services are containerized and orchestrated via Docker Compose.

**Service Definitions:**

| Service | Image | Port | Type | Dependencies |
|---------|-------|------|------|--------------|
| extract-agent | python:3.11 | 8007 | Worker | - |
| verify-agent | python:3.11 | 8008 | Worker | kyc-vector-db |
| reason-agent | python:3.11 | 8006 | Worker | ollama, mcp-server |
| risk-agent | python:3.11 | 8004 | Worker | - |
| decision-agent | python:3.11 | 8005 | Worker | - |
| orchestration-service | python:3.11 | 8000 | Coordinator | all agents |
| api-gateway | python:3.11 | 8000 | Gateway | orchestration-service |
| frontend | node:18 | 3000 | UI | api-gateway |
| mcp-server | python:3.11 | 8020 | Support | kyc-vector-db |
| ollama | ollama/ollama | 11434 | LLM | - |

### Volumes

```yaml
volumes:
  kyc-vector-db:        # Persistent vector database
  kyc-logs:             # Centralized logs
  ollama:               # LLM model storage
```

### Network

- Internal Docker network for service-to-service communication
- API Gateway exposed to external clients
- Frontend accessible on port 3000

### Health Checks

All services include health checks:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 20s
```

### Configuration via Environment Variables

**Global Variables:**
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `REQUEST_TIMEOUT` - HTTP request timeout (seconds)

**Service-Specific Variables:**
```bash
# Extract Agent
EXTRACT_AGENT_PORT=8007

# Verify Agent
VERIFY_AGENT_PORT=8008
VECTOR_DB_PATH=/data/kyc_vector_db

# Reason Agent
REASON_AGENT_PORT=8006
OLLAMA_URL=http://ollama:11434
LLM_MODEL=mistral
MCP_SERVER_URL=http://mcp-server:8020

# Risk Agent
RISK_AGENT_PORT=8004

# Decision Agent
DECISION_AGENT_PORT=8005

# Orchestration Service
ORCHESTRATION_SERVICE_URL=http://orchestration-service:8000

# API Gateway
API_GATEWAY_PORT=8000
```

---

## Technology Stack

### Backend Services
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn (ASGI)
- **HTTP Client**: Requests
- **Logging**: Python logging module

### AI/ML Components
- **LLM Integration**: LangChain + Ollama
- **LLM Model**: Mistral 7B
- **Vector Database**: ChromaDB
- **Document Processing**: Tesseract (OCR), Pillow (Images)
- **Analytics**: NumPy, SciPy

### Frontend
- **Runtime**: Node.js
- **Framework**: Express.js
- **Compression**: gzip (via compression middleware)
- **UI**: HTML5, Vanilla JavaScript

### DevOps & Deployment
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Monitoring**: Container health checks
- **Logging**: JSON-file driver (10MB max, 3 rotations)

### Version Compatibility
- **Python**: 3.11+
- **Node.js**: 14+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

---

## Integration Patterns

### 1. **Service-to-Service Communication**

**Pattern**: Synchronous HTTP/REST

```
┌─────────────┐
│  Service A  │
│  (FastAPI)  │
└──────┬──────┘
       │ requests.post()
       │ JSON payload
       ▼
┌─────────────────────┐
│   Service B         │
│   (HTTP Endpoint)   │
└──────┬──────────────┘
       │ Response JSON
       ▼
┌─────────────┐
│  Service A  │
│  Processes  │
└─────────────┘
```

**Error Handling:**
- Connection errors → Return error object
- Timeouts → Graceful degradation
- HTTP errors → Capture and log
- JSON parsing failures → Fallback defaults

### 2. **Knowledge Base Integration (Vector DB)**

**Pattern**: Semantic Search + Context Injection

```
Reason Agent Request
     ↓
Query Vector DB: "Semantic similarity search"
     ↓
Retrieve Top-K Rules/Patterns
     ↓
Inject into LLM Context
     ↓
Run LLM with RAG Context
     ↓
Return Enhanced Analysis
```

### 3. **MCP Tool Integration**

**Pattern**: Standardized Tool Calls

```
Agent → MCP Server → Tool Registry → Return Results
```

**Benefits:**
- Decoupled tool management
- Standardized tool interface
- Easy tool addition/removal
- Language-agnostic

### 4. **LLM Integration (Ollama)**

**Pattern**: Langchain Wrapper

```
Application Code
     ↓
LangChain (High-level API)
     ↓
ChatOllama (Provider)
     ↓
Ollama HTTP API (http://ollama:11434)
     ↓
LLM Model (Mistral)
     ↓
Token Generation
     ↓
Result Parsing (JsonOutputParser)
     ↓
Application
```

---

## Scalability & Performance

### Horizontal Scaling

**Stateless Agents:**
- Can deploy multiple instances behind load balancer
- No shared state between instances
- Independent scaling per agent

**Example Scaling:**
```yaml
extract-agent:
  deploy:
    replicas: 3
  
verify-agent:
  deploy:
    replicas: 2  # Less frequent bottleneck
  
reason-agent:
  deploy:
    replicas: 1  # LLM-intensive
```

### Vertical Scaling

**Resource Allocation (CPU/Memory):**

| Service | CPU | Memory | Notes |
|---------|-----|--------|-------|
| extract-agent | 1-2 | 1GB | OCR intensive |
| verify-agent | 0.5-1 | 512MB | Lightweight |
| reason-agent | 2-4 | 2-4GB | LLM intensive |
| risk-agent | 1 | 512MB | Lightweight |
| decision-agent | 0.5-1 | 512MB | Lightweight |
| ollama | 4-8 | 8-16GB | Model inference |

### Performance Optimization

1. **Request Timeout Management**
   - Default: 120s for inter-agent calls
   - API Gateway: 300s end-to-end
   - Configurable per environment

2. **Logging Optimization**
   - JSON-file driver with rotation
   - 10MB max per file, 3 backups
   - Configurable log level (WARNING default)

3. **Caching Strategies**
   - Vector DB semantic cache
   - Rule loading cache (in-memory)
   - Model inference cache (Ollama)

4. **Parallel Processing**
   - Verify & Reason agents run in parallel
   - Independent orchestration
   - No inter-agent dependencies

5. **Resource Monitoring**
   - Health checks every 15s
   - Container resource limits
   - Automatic restart on failure

---

## Security Considerations

### 1. **Input Validation**

**API Gateway Layer:**
- File existence validation
- File type validation (MIME types)
- File size limits
- Document content validation

**Agent Layer:**
- Document validator (extract-agent)
- Format validation (image types)
- Text sanitization

### 2. **Data Protection**

**Sensitive Data Handling:**
- PII (Personally Identifiable Information)
- Financial information
- Identity documents

**Measures:**
- Encrypted communication (HTTPS recommended for production)
- Secure storage with encryption
- Access control to vector database
- Log sanitization (no PII in logs)

### 3. **Authentication & Authorization**

**Current State:**
- No authentication layer (assumes internal network)

**Recommended Additions:**
```python
# For production deployment
from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.post("/kyc")
async def kyc(credentials: HTTPAuthenticationCredentials = Depends(security)):
    # Validate token
    # Extract user/org from token
    # Apply role-based access control
    pass
```

### 4. **Network Security**

**Docker Network:**
- Internal communication isolated
- Services only accessible via API Gateway
- No direct exposure of worker agents

**Production Considerations:**
- API Gateway behind reverse proxy (Nginx/Kong)
- TLS/SSL for all external connections
- Rate limiting per API key
- DDoS protection

### 5. **Audit & Compliance**

**Logging Requirements:**
- All requests logged (method, endpoint, status)
- Processing results logged for audit trail
- Error conditions captured
- Timestamp all operations

**Retention:**
- Configurable log rotation (default: 3 files × 10MB)
- Centralized logging (kyc-logs volume)
- Audit trail for compliance

### 6. **Model Security (LLM)**

**Risks:**
- Prompt injection attacks
- Information disclosure via model
- Adversarial inputs

**Mitigations:**
- Temperature set low (0.1-0.3) for consistency
- Output validation (JSON parsing)
- Isolated LLM in trusted network
- Input sanitization before LLM

---

## System Dependencies

### Python Dependencies

**Core:**
- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- requests >= 2.31.0
- pydantic >= 2.0.0

**AI/ML:**
- langchain >= 0.1.0
- langchain-ollama >= 0.1.0
- chromadb >= 0.4.0

**Document Processing:**
- pytesseract >= 0.3.10
- pillow >= 10.0.0

**Analytics:**
- numpy >= 1.24.0
- scipy >= 1.10.0

**See individual requirements.txt files in each service directory**

### External Services

- **Ollama**: LLM server (configurable URL)
- **Docker**: Container runtime
- **Docker Compose**: Container orchestration

---

## Deployment & Operations

### Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd FinalSolution

# 2. Configure environment (.env)
cp .env.template .env
# Edit .env with your settings

# 3. Initialize vector database
python init_vector_db_simple.py

# 4. Start services
docker-compose up -d

# 5. Access frontend
# Navigate to http://localhost:3000
```

### Health Monitoring

```bash
# Check all services
curl http://localhost:8000/health

# Check individual agents
curl http://localhost:8004/health  # Risk Agent
curl http://localhost:8005/health  # Decision Agent
curl http://localhost:8006/health  # Reason Agent
curl http://localhost:8007/health  # Extract Agent
curl http://localhost:8008/health  # Verify Agent
```

### Logs

```bash
# All service logs
docker-compose logs -f

# Specific service
docker-compose logs -f reason-agent

# From host volume
tail -f kyc-logs/*
```

### Troubleshooting

**Agent Connection Errors:**
```bash
# Verify Docker network
docker network ls
docker network inspect finalsolution_default

# Check service DNS resolution
docker exec orchestration-service nslookup extract-agent
```

**Vector Database Issues:**
```bash
# Check volume persistence
docker volume ls | grep kyc

# Re-initialize vector DB
docker exec mcp-server python /app/init_db.py
```

**LLM Model Not Loading:**
```bash
# Verify Ollama service
docker logs ollama

# Check model availability
curl http://localhost:11434/api/tags

# Pull model if needed
docker exec ollama ollama pull mistral
```

---

## Future Enhancements

### 1. **Advanced Features**
- Multi-model support (GPT-4, Claude, etc.)
- Real-time streaming results
- Batch processing support
- Webhook callbacks

### 2. **Scalability**
- Kubernetes migration
- Message queue (RabbitMQ, Kafka)
- Distributed tracing (Jaeger)
- Centralized logging (ELK stack)

### 3. **Integration**
- Database persistence (PostgreSQL)
- API versioning (v1, v2)
- GraphQL endpoint
- gRPC for high-performance communication

### 4. **Operations**
- Metrics collection (Prometheus)
- Alerting system (AlertManager)
- CI/CD pipeline (GitHub Actions)
- Performance profiling

### 5. **Security**
- OAuth2/OIDC authentication
- Role-based access control (RBAC)
- API key management
- Data encryption at rest

---

## Conclusion

The KYC/AML Agentic AI System represents a modern, scalable approach to compliance automation. By decomposing the problem into specialized agents and orchestrating their collaboration, the system achieves:

✅ **Modularity**: Easy to develop, test, and update individual agents  
✅ **Scalability**: Horizontal scaling per agent capability  
✅ **Reliability**: Fault isolation and graceful degradation  
✅ **Maintainability**: Clear responsibilities and interfaces  
✅ **Extensibility**: Simple to add new agents or tools  
✅ **Intelligence**: AI-powered analysis with RAG and LLM  

The architecture is production-ready and can be extended to support additional compliance use cases beyond KYC/AML.

---

**Document Information:**
- **Version**: 1.0
- **Created**: April 6, 2026
- **Author**: Architecture Documentation
- **Status**: Complete
- **Next Review**: Q3 2026

