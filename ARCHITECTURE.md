# 🏗️ KYC Agentic AI - Complete Architecture Documentation

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Component Interactions](#component-interactions)
6. [Validation Pipeline](#validation-pipeline)
7. [Deployment Architecture](#deployment-architecture)
8. [Technology Stack](#technology-stack)

---

## 🎯 System Overview

### Purpose
KYC (Know Your Customer) Agentic AI is an intelligent, automated system for customer identity verification and risk assessment using multiple independent AI agents working in an orchestrated pipeline.

### Architecture Pattern
**Event-Driven Microservices with AI Orchestration**
- Independent agents (microservices) handle specific KYC tasks
- Central orchestrator coordinates the workflow
- API Gateway provides unified interface
- Vector DB + RAG for intelligent decision making

### Key Principles
- ✅ **Modularity** - Each agent has single responsibility
- ✅ **Scalability** - Independent scaling of agents
- ✅ **Resilience** - Health checks and graceful degradation
- ✅ **Intelligence** - AI-powered validation and reasoning
- ✅ **Transparency** - Complete audit trail of all operations

---

## 🏢 Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  (Frontend - Web UI)                                         │
│  Port: 3000                                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              API GATEWAY LAYER                               │
│  (Single Entry Point)                                        │
│  Port: 8000                                                  │
│  - Request routing                                           │
│  - Authentication                                            │
│  - Response formatting                                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│           ORCHESTRATION LAYER                                │
│  (Workflow Coordination)                                     │
│  Port: 8010                                                  │
│  - Agent sequencing                                          │
│  - State management                                          │
│  - Decision logic                                            │
└──┬─────────────────┬──────────────────┬────────────────────┬┘
   │                 │                  │                    │
┌──▼──┐    ┌────────▼────┐    ┌───────▼────┐    ┌──────────▼──┐
│ E   │    │ V           │    │ R          │    │ D           │
│ A   │    │ E           │    │ I          │    │ E           │
│ G   │    │ R           │    │ S          │    │ C           │
│     │    │ I           │    │ K          │    │ I           │
└──┬──┘    └────────┬────┘    └───────┬────┘    └──────────┬──┘
   │                 │                 │                   │
└──────────────────────────────────────────────────────────┘
        AGENT LAYER (Microservices)
        - Extract Agent
        - Verify Agent
        - Reason Agent
        - Risk Agent
        - Decision Agent

        SUPPORT SERVICES:
        - MCP Server (RAG + Knowledge Base)
        - Vector DB (Embeddings + Retrieval)
```

---

## 🔧 Core Components

### 1. **API GATEWAY** (Port 8000)
**Type**: FastAPI Service
**Responsibility**: Single entry point for all external requests

```
Functions:
├─ Request routing to orchestration service
├─ Request validation
├─ Response formatting
├─ Error handling
├─ Health monitoring
└─ Authentication (future)

Interface:
├─ POST /kyc/validate - Initiate KYC process
├─ GET /kyc/status/{request_id} - Check status
├─ GET /health - Service health
└─ GET /metrics - Performance metrics
```

### 2. **ORCHESTRATION SERVICE** (Port 8010)
**Type**: FastAPI Workflow Engine
**Responsibility**: Coordinate agent pipeline execution

```
Functions:
├─ Sequencing agents in correct order
├─ Managing state between agents
├─ Handling agent responses
├─ Error recovery and retries
├─ Logging and audit trails
├─ Performance tracking
└─ Decision consolidation

Workflow:
1. Receive request from API Gateway
2. Initialize extraction process
3. Verify extracted data
4. Perform reasoning analysis
5. Assess risk profile
6. Make final KYC decision
7. Return consolidated result
```

### 3. **EXTRACT AGENT** (Port 8001)
**Type**: FastAPI Service
**Responsibility**: Extract customer information from multiple sources

```
Capabilities:
├─ Document parsing (ID, Passport, PAN, Aadhar)
├─ Data normalization
├─ Field extraction
├─ Format standardization
├─ Confidence scoring
└─ Error flagging

Input: Raw customer data
Output: Structured extracted data with confidence scores
Performance: ~100-200ms per request
```

### 4. **VERIFY AGENT** (Port 8002)
**Type**: FastAPI Service
**Responsibility**: Verify extracted data accuracy

```
Capabilities:
├─ Cross-field validation
├─ Format verification
├─ Range checking
├─ Consistency validation
├─ Database lookups
├─ Real-time verification APIs
└─ Fraud pattern detection

Input: Extracted data from Extract Agent
Output: Verification status + confidence scores
Performance: ~200-500ms per request
```

### 5. **REASON AGENT** (Port 8003)
**Type**: FastAPI + LLM Service (Ollama)
**Responsibility**: Intelligent analysis using AI reasoning

```
Capabilities:
├─ Natural language analysis
├─ Context understanding
├─ Anomaly detection
├─ Policy compliance checking
├─ RAG-based knowledge retrieval
├─ Explanation generation
└─ Decision support

Input: Verified data + context
Output: Reasoning analysis + recommendations
Performance: ~1-3s per request (LLM dependent)
```

### 6. **RISK AGENT** (Port 8004)
**Type**: FastAPI Service
**Responsibility**: Assess customer risk profile

```
Capabilities:
├─ Risk scoring algorithms
├─ Fraud probability calculation
├─ Sanctions list checking
├─ PEP (Politically Exposed Person) checking
├─ Historical risk data lookup
├─ Compliance rule evaluation
└─ Risk categorization

Input: All previous data + external data
Output: Risk score + risk category + flags
Performance: ~300-600ms per request
```

### 7. **DECISION AGENT** (Port 8005)
**Type**: FastAPI Service
**Responsibility**: Make final KYC approval/rejection decision

```
Capabilities:
├─ Multi-factor decision logic
├─ Threshold-based rules
├─ Exception handling
├─ Policy enforcement
├─ Case escalation
├─ Audit logging
└─ Decision explanation

Input: All agent outputs + risk profile
Output: APPROVED/REJECTED/REVIEW_REQUIRED + reason
Performance: ~50-100ms per request
```

### 8. **VALIDATION PIPELINE** (Ports 8100-8103)
**Type**: Multi-tier Validation System
**Responsibility**: Ensure data quality throughout the process

```
Architecture:
┌─────────────────────────────────────────┐
│ VALIDATION ORCHESTRATOR (8100)          │
│ Intelligent chain coordinator            │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐┌────────┐┌────────┐
│Validator-1│Validator-2│Validator-3
│(8101)     │(8102)      │(8103)
│Pattern    │Fuzzy       │AI/Ollama
│Validation │Matching    │Validation
└────────┘└────────┘└────────┘

Validation Flow:
├─ V1 (Fast): Pattern matching (50-100ms)
├─ V2 (Medium): Fuzzy matching if V1 fails (100-200ms)
└─ V3 (Smart): Ollama LLM if V2 fails (1-5s)

Fallback: If V1 fails → try V2 → try V3 → REJECT if all fail
```

### 9. **MCP SERVER** (Port 8020)
**Type**: FastAPI + LLM Tools Server
**Responsibility**: Provide RAG and tool integration for agents

```
Capabilities:
├─ Knowledge base retrieval
├─ Embedding generation
├─ Semantic search
├─ Document similarity
├─ Policy/rules lookup
└─ Tool calling interface

Features:
├─ Vector DB integration
├─ Retrieval-Augmented Generation (RAG)
├─ Context enrichment
└─ Tool calling for external APIs
```

### 10. **VECTOR DATABASE** (kyc_vector_db/)
**Type**: ChromaDB
**Responsibility**: Store and retrieve embeddings for RAG

```
Data Stored:
├─ KYC Rules (kyc_rules.json)
├─ Fraud Patterns (fraud_patterns.json)
├─ Policy Documents (indexed)
├─ Customer Historical Data
└─ Decision Patterns

Usage:
├─ Reason Agent uses for context
├─ Risk Agent uses for pattern matching
├─ MCP Server provides access
└─ Supports similarity search

Index: index.json
Metadata: metadata/
```

### 11. **FRONTEND** (Port 3000)
**Type**: Node.js Web Server
**Responsibility**: User interface for KYC application

```
Features:
├─ Customer information input
├─ Real-time status tracking
├─ Document upload
├─ Result display
├─ Audit trail viewing
└─ Admin dashboard

Tech Stack:
├─ HTML/CSS/JavaScript
├─ Node.js server
└─ Connects to API Gateway
```

---

## 📊 Data Flow

### Complete KYC Request Flow

```
1. USER INITIATES REQUEST
   └─→ Frontend (3000) receives customer data

2. API GATEWAY (8000)
   └─→ Receives request from frontend
   └─→ Validates request format
   └─→ Routes to Orchestration Service

3. ORCHESTRATION SERVICE (8010)
   └─→ Creates KYC request context
   └─→ Initiates agent pipeline
   └─→ Tracks state transitions

4. EXTRACT AGENT (8001)
   └─→ Receives customer data
   └─→ Parses documents
   └─→ Extracts fields
   └─→ Normalizes data
   └─→ Returns: {extracted_data, confidence_scores}

5. VERIFY AGENT (8002)
   └─→ Receives extracted data
   └─→ Validates each field
   └─→ Checks consistency
   └─→ Performs lookups
   └─→ Returns: {verification_status, flags}

6. MCP SERVER (8020)
   └─→ Provides context to Reason Agent
   └─→ Retrieves relevant policies
   └─→ Provides embeddings
   └─→ Returns context data

7. REASON AGENT (8003)
   └─→ Receives verified data + context
   └─→ Queries MCP Server for knowledge
   └─→ Uses Ollama LLM for analysis
   └─→ Generates explanations
   └─→ Returns: {analysis, recommendations}

8. RISK AGENT (8004)
   └─→ Receives all previous data
   └─→ Queries Vector DB for patterns
   └─→ Calculates risk scores
   └─→ Checks sanctions/PEP lists
   └─→ Returns: {risk_score, risk_category, flags}

9. DECISION AGENT (8005)
   └─→ Receives all agent outputs
   └─→ Applies decision logic
   └─→ Enforces policies
   └─→ Makes final decision
   └─→ Returns: {decision, reason, actions}

10. ORCHESTRATION SERVICE
    └─→ Consolidates all results
    └─→ Logs audit trail
    └─→ Calculates metrics
    └─→ Returns consolidated result

11. API GATEWAY
    └─→ Formats response
    └─→ Returns to Frontend

12. FRONTEND
    └─→ Displays decision
    └─→ Shows supporting details
    └─→ Provides audit trail
```

### Request/Response Example

**Request:**
```json
{
  "customer_id": "CUST_12345",
  "documents": [
    {
      "type": "PASSPORT",
      "file": "base64_encoded_document"
    }
  ],
  "personal_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210"
  }
}
```

**Response:**
```json
{
  "request_id": "REQ_67890",
  "decision": "APPROVED",
  "confidence": 0.95,
  "extracted_data": {
    "name": "John Doe",
    "pan": "AAAA0001A",
    "aadhar": "123456789012"
  },
  "verification_status": "VERIFIED",
  "risk_score": 15,
  "risk_category": "LOW",
  "reasoning": "Customer data verified. No red flags detected.",
  "actions": ["APPROVE", "SEND_WELCOME_EMAIL"],
  "timestamp": "2026-04-01T10:30:00Z",
  "audit_trail": [...]
}
```

---

## 🔄 Component Interactions

### Agent Execution Sequence

```
Timeline:
┌─────────────────────────────────────────────────────────────┐
│ T=0ms: Request arrives at API Gateway                       │
├─────────────────────────────────────────────────────────────┤
│ T=10ms: Orchestration Service received                      │
├─────────────────────────────────────────────────────────────┤
│ T=50ms: Extract Agent starts (parallel with validators)     │
│ T=50ms: Validation Pipeline starts                          │
├─────────────────────────────────────────────────────────────┤
│ T=200ms: Extract Agent completes (150ms)                    │
│ T=150ms: Validation checks complete (100ms)                 │
├─────────────────────────────────────────────────────────────┤
│ T=300ms: Verify Agent starts                                │
├─────────────────────────────────────────────────────────────┤
│ T=700ms: Verify Agent completes (400ms)                     │
├─────────────────────────────────────────────────────────────┤
│ T=750ms: Reason Agent starts (queries MCP)                  │
├─────────────────────────────────────────────────────────────┤
│ T=2500ms: Reason Agent completes (1750ms with LLM)          │
├─────────────────────────────────────────────────────────────┤
│ T=2550ms: Risk Agent starts                                 │
│ T=2550ms: Queries Vector DB for patterns                    │
├─────────────────────────────────────────────────────────────┤
│ T=3150ms: Risk Agent completes (600ms)                      │
├─────────────────────────────────────────────────────────────┤
│ T=3200ms: Decision Agent starts                             │
├─────────────────────────────────────────────────────────────┤
│ T=3300ms: Decision Agent completes (100ms)                  │
├─────────────────────────────────────────────────────────────┤
│ T=3350ms: Orchestration consolidates results                │
├─────────────────────────────────────────────────────────────┤
│ T=3400ms: Response sent to API Gateway                      │
├─────────────────────────────────────────────────────────────┤
│ T=3420ms: Response sent to Frontend                         │
│ TOTAL TIME: ~3.4 seconds                                    │
└─────────────────────────────────────────────────────────────┘
```

### Inter-Service Communication

```
Communication Pattern: Request-Response over HTTP

API Gateway (8000)
    │
    └─→ POST http://orchestration-service:8010/process
            │
            ├─→ POST http://extract-agent:8001/extract
            │
            ├─→ POST http://verify-agent:8002/verify
            │
            ├─→ GET http://mcp-server:8020/context (for Reason)
            │   └─→ Queries Vector DB internally
            │
            ├─→ POST http://reason-agent:8003/analyze
            │
            ├─→ POST http://risk-agent:8004/assess
            │
            ├─→ POST http://decision-agent:8005/decide

---

## 🚀 Deployment Architecture

### Docker Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Host (kyc-network)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Frontend    │  │ API Gateway  │  │ Orchestration│      │
│  │  (3000)      │  │ (8000)       │  │ (8010)       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │Extract │ │ Verify │ │ Reason │ │  Risk  │ │Decision│   │
│  │ (8001) │ │ (8002) │ │ (8003) │ │ (8004) │ │ (8005) │   │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │MCP Server    │  │ Validation   │  │ Vector DB    │      │
│  │(8020)        │  │ Orchestrator │  │ (embedded)   │      │
│  │              │  │ (8100)       │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Validators:                                                 │
│  ┌────────┐ ┌────────┐ ┌────────┐                           │
│  │Val-1   │ │Val-2   │ │Val-3   │                           │
│  │(8101)  │ │(8102)  │ │(8103)  │                           │
│  └────────┘ └────────┘ └────────┘                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
        All services on kyc-network bridge
        Health checks every 15s
        Auto-restart on failure
```

### Scaling Architecture

```
Horizontal Scaling:
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer                             │
├─────────────────────────────────────────────────────────────┤
│   ↓               ↓               ↓                          │
│  API GW-1       API GW-2       API GW-3                     │
│   ↓               ↓               ↓                          │
│ Orch-1          Orch-2          Orch-3                      │
│   ├─────┬─────┬──────┐          similar                     │
│   │ Ext │Ver │Reason│  ...      structure                   │
│   └─────┴─────┴──────┘                                      │
└─────────────────────────────────────────────────────────────┘

Agent-Specific Scaling:
- Extract Agent: Scale for I/O bound operations
- Reason Agent: Fewer instances (LLM resource intensive)
- Risk Agent: Scale for pattern matching
- Decision Agent: Scale minimally (CPU intensive)
```

---

## 💻 Technology Stack

### Services
- **Framework**: FastAPI (Python 3.11)
- **Web Server**: Uvicorn
- **Documentation**: Swagger/OpenAPI
- **Health Checks**: HTTP endpoint checks

### Data & Storage
- **Vector DB**: ChromaDB (embedded)
- **Data Format**: JSON
- **Persistence**: File-based (kyc_vector_db/)

### AI/ML
- **LLM Service**: Ollama (local)
- **Default Model**: Mistral
- **Embedding**: Via Ollama

### Frontend
- **Runtime**: Node.js
- **Port**: 3000
- **Communication**: REST API calls to API Gateway

### DevOps & Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose
- **Networking**: Docker bridge network (kyc-network)
- **Health**: Container health checks + curl
- **Logging**: Structured JSON logs

### Agents Ports Mapping

| Service | External Port | Internal Port | Purpose |
|---------|---------------|---------------|---------|
| Frontend | 3000 | 3000 | Web UI |
| API Gateway | 8000 | 8000 | Entry point |
| Extract Agent | 8001 | 8000 | Data extraction |
| Verify Agent | 8002 | 8000 | Data verification |
| Reason Agent | 8003 | 8000 | AI reasoning |
| Risk Agent | 8004 | 8000 | Risk assessment |
| Decision Agent | 8005 | 8000 | Final decision |
| Orchestration | 8010 | 8010 | Workflow engine |
| MCP Server | 8020 | 8020 | Tools/RAG |
| Validation Orch | 8100 | 8001 | Validation coord |
| Validator-1 | 8101 | 8001 | Pattern validator |
| Validator-2 | 8102 | 8002 | Fuzzy validator |
| Validator-3 | 8103 | 8003 | AI validator |

---

## 🔐 Security Considerations

### Network Security
- All services on internal Docker network
- External access only through API Gateway
- Port restrictions and firewalls

### Data Security
- Request validation at API Gateway
- Input sanitization in each agent
- Audit logging for all operations
- TraceID for request correlation

### Service Security
- Health checks for availability
- Auto-restart on failure
- Resource limits per container
- Environment-based configuration

---

## 📈 Performance Characteristics

### Request Processing Timeline
- **Extract**: 150ms (document parsing)
- **Verify**: 400ms (validation + lookups)
- **Reason**: 1750ms (LLM analysis)
- **Risk**: 600ms (scoring + checks)
- **Decision**: 100ms (logic + rules)
- **Overhead**: ~400ms (orchestration + network)
- **Total**: ~3400ms average

### Scalability
- **Concurrent Requests**: Limited by orchestrator
- **Throughput**: ~20 requests/minute (3.4s/request)
- **Agent Scaling**: Independent scaling possible
- **Bottleneck**: LLM-based Reason Agent

---

## 📊 System Metrics

### Monitoring Points
- Service health (availability)
- Request latency (p50, p95, p99)
- Error rates (by agent)
- Decision distribution (approved/rejected)
- Validation tier distribution
- Resource usage (CPU, memory)

### Logging
- Structured JSON format
- TraceID for correlation
- Timestamp in ISO 8601
- Level: INFO, WARNING, ERROR, DEBUG

---

## 🎯 Key Design Decisions

### Why Microservices?
- Independent scaling per agent
- Fault isolation
- Easy to add/remove agents
- Technology flexibility

### Why Orchestrator Service?
- Central coordination point
- State management
- Simplified client interface
- Easier to change workflow

### Why Validation Pipeline?
- Multi-tiered approach for reliability
- Fast path for good data
- AI fallback for edge cases
- Ensures data quality

### Why Vector DB?
- Semantic search capabilities
- Historical pattern matching
- Efficient policy lookup
- RAG support for Reason Agent

---

## 🚀 Deployment Process

### Local Deployment
```bash
docker-compose up -d
# Services start on ports 3000, 8000-8005, 8010, 8020, 8100-8103
```

### Docker Hub Deployment
```bash
docker pull username/kyc-orchestrator:latest
docker pull username/kyc-extract-agent:latest
# etc...
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment
```bash
kubectl apply -f kube-manifests/
# Services scheduled across nodes
# Auto-scaling based on metrics
# Rolling updates for zero downtime
```

---

## 🔍 Troubleshooting

### Service Unavailable
1. Check service health: `curl http://localhost:8000/health`
2. View logs: `docker logs service-name`
3. Check network: `docker network inspect kyc-network`
4. Restart service: `docker restart service-name`

### Slow Response Time
1. Check Reason Agent (LLM bottleneck)
2. Monitor resource usage: `docker stats`
3. Check Vector DB queries
4. Scale agents horizontally

### High Error Rates
1. Check input validation
2. Review agent logs for errors
3. Check external service availability
4. Verify model availability (Ollama)

---

## 📚 Related Documentation

- **README.md** - Project overview
- **DEPLOYMENT_GUIDE.md** - Detailed deployment
- **QUICK_REFERENCE.md** - Quick commands
- **docker-compose.yml** - Service definitions

---

**This is the complete architecture of the KYC Agentic AI system - a modern, scalable, and intelligent customer verification platform.** ✅

