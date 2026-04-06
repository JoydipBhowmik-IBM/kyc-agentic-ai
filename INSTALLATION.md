# KYC Agentic AI - Installation Guide

## Prerequisites

- Docker & Docker Compose (version 3.8+)
- Python 3.11+ (for local development)
- 4GB RAM minimum, 8GB recommended
- Git

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd kyc-agentic-ai
```

### 2. Configure Environment
```bash
# Copy template to .env file
cp .env.template .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Key Environment Variables:**
```bash
LOG_LEVEL=WARNING              # Set to INFO for debugging
EXTRACT_AGENT_PORT=8001
VERIFY_AGENT_PORT=8002
REASON_AGENT_PORT=8003
RISK_AGENT_PORT=8004
DECISION_AGENT_PORT=8005
ORCHESTRATION_PORT=8006
API_GATEWAY_PORT=8000
MCP_SERVER_PORT=8010
OLLAMA_URL=http://ollama:11434
OLLAMA_PORT=11434
```

### 3. Start Services with Docker Compose
```bash
# Start all services (background)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access the Application

**Frontend UI:**
- URL: `http://localhost:3000`

**API Gateway:**
- URL: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`

**Individual Services:**
- Extract Agent: `http://localhost:8001`
- Verify Agent: `http://localhost:8002`
- Reason Agent: `http://localhost:8003`
- Risk Agent: `http://localhost:8004`
- Decision Agent: `http://localhost:8005`
- Orchestration Service: `http://localhost:8006`
- MCP Server: `http://localhost:8010`

## Local Development Setup

### 1. Create Python Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Install all agent dependencies
pip install -r agents/extract-agent/requirements.txt
pip install -r agents/verify-agent/requirements.txt
pip install -r agents/reason-agent/requirements.txt
pip install -r agents/risk-agent/requirements.txt
pip install -r agents/decision-agent/requirements.txt
pip install -r orchestration-service/requirements.txt
pip install -r api-gateway/requirements.txt
pip install -r mcp-server/requirements.txt
```

### 3. Run Individual Services (Terminal per service)
```bash
# Terminal 1 - Extract Agent
cd agents/extract-agent
python -m uvicorn main:app --reload --port 8001

# Terminal 2 - Verify Agent
cd agents/verify-agent
python -m uvicorn main:app --reload --port 8002

# Terminal 3 - Reason Agent
cd agents/reason-agent
python -m uvicorn main:app --reload --port 8003

# Terminal 4 - Risk Agent
cd agents/risk-agent
python -m uvicorn main:app --reload --port 8004

# Terminal 5 - Decision Agent
cd agents/decision-agent
python -m uvicorn main:app --reload --port 8005

# Terminal 6 - Orchestration Service
cd orchestration-service
python -m uvicorn main:app --reload --port 8006

# Terminal 7 - API Gateway
cd api-gateway
python -m uvicorn main:app --reload --port 8000

# Terminal 8 - Ollama (if running locally)
ollama serve

# Terminal 9 - MCP Server
cd mcp-server
python -m uvicorn main:app --reload --port 8010
```

## Docker Compose Services

The `docker-compose.yml` includes:

1. **Extract Agent** - Document OCR and text extraction
2. **Verify Agent** - Document verification and validation
3. **Reason Agent** - AI-powered analysis with RAG
4. **Risk Agent** - Risk assessment and scoring
5. **Decision Agent** - Final decision making
6. **Orchestration Service** - Workflow orchestration
7. **API Gateway** - API endpoint manager
8. **MCP Server** - Model Context Protocol server
9. **Ollama** - Local LLM inference engine

## Logging Configuration

Control log verbosity with `LOG_LEVEL` environment variable:

```bash
# Production (minimal logs - only errors/warnings)
export LOG_LEVEL=WARNING
docker-compose up

# Development (detailed logs)
export LOG_LEVEL=INFO
docker-compose up

# Debugging (very detailed)
export LOG_LEVEL=DEBUG
docker-compose up
```

## Troubleshooting

### Services won't start
```bash
# Check Docker status
docker ps
docker-compose ps

# View logs
docker-compose logs <service-name>

# Rebuild containers
docker-compose build --no-cache
docker-compose up
```

### Vector Database Issues
```bash
# Reinitialize vector database
rm -rf kyc_vector_db/
docker-compose restart mcp-server
```

### Port Conflicts
Edit `.env` file to change ports:
```bash
EXTRACT_AGENT_PORT=9001
VERIFY_AGENT_PORT=9002
# etc...
```

### Out of Memory
Increase Docker memory limit or reduce concurrent operations.

## Deployment

For production deployment:

1. Update `.env` with production values
2. Set `LOG_LEVEL=WARNING` for minimal logging
3. Use a reverse proxy (nginx) for the API Gateway
4. Enable SSL/TLS certificates
5. Configure monitoring and alerting
6. Use persistent volumes for data

## Additional Resources

- **Architecture**: See `ARCHITECTURE.md` for system design details
- **API Documentation**: Available at `http://localhost:8000/docs` (Swagger UI)
- **Support**: Check service logs for detailed error messages

## Testing

### Upload a PAN Document
1. Open `http://localhost:3000`
2. Upload a clear PAN card image
3. Monitor processing through pipeline
4. View decision result

### Test PAN Numbers (Mock API)
- `CYMPB5839A` (BORUGULA SURESH) → APPROVED
- `BWZPS1234R` (TWITTERPREET SINGH) → REJECTED (not in approved list)
- Unknown PANs → REJECTED

## Performance

- **Extract Agent**: ~50-500ms (depends on image size)
- **Verify Agent**: ~100-200ms
- **Reason Agent**: ~500-2000ms (depends on LLM model)
- **Risk Agent**: ~100-300ms
- **Decision Agent**: ~50-100ms
- **Total Pipeline**: ~1-3 seconds

## Security

- Change default ports in production
- Use environment variables for secrets
- Enable authentication on API Gateway
- Use HTTPS/SSL in production
- Regularly update Docker images

## License

[Your License Here]

## Support

For issues or questions, please open an issue in the repository or contact the development team.
