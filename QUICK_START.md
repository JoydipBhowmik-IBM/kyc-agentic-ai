# KYC/AML Agentic AI System - Quick Start Guide

**TL;DR - Get running in 5 minutes!**

---

## 🚀 Quick Start (Docker Compose)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 16GB RAM minimum
- Port 3000, 8000, 8003-8008, 8010, 8020, 11434 available

### Installation (5 steps)

```bash
# 1. Clone/extract repository
cd kyc-agentic-ai

# 2. Copy environment config
cp .env.example .env

# 3. Initialize vector database
python3 init_vector_db_simple.py

# 4. Start all services
docker-compose up -d

# 5. Wait 2-3 minutes for startup...
docker-compose ps
```

### Access Application

```
Frontend:    http://localhost:3000
API Docs:    http://localhost:8000/docs
Ollama:      http://localhost:11434
```

### Verify Health

```bash
curl http://localhost:8000/health
curl http://localhost:3000/health
```

---

## ⚙️ Common Commands

```bash
# View logs (real-time)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api-gateway

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# Check service status
docker-compose ps

# View resource usage
docker stats

# Run health diagnostics
for port in 3000 8000 8003 8004 8005 8007 8008 8010 8020 11434; do
  echo -n "Port $port: "
  curl -s http://localhost:$port/health | grep -q healthy && echo "✓" || echo "✗"
done
```

---

## 🔧 Troubleshooting

### Services not starting?

```bash
# Check logs
docker-compose logs

# Common issues:
# 1. Port already in use → Change port in .env
# 2. Out of memory → Allocate more RAM to Docker
# 3. Ollama not ready → Wait 5+ minutes for model download
```

### Can't upload documents?

```bash
# Check API Gateway
curl http://localhost:8000/health

# Check Frontend
curl http://localhost:3000/health

# View detailed logs
docker-compose logs api-gateway
docker-compose logs orchestration-service
```

### Ollama model not loading?

```bash
# Check Ollama status
docker logs ollama

# Manually pull model
docker exec ollama ollama pull mistral

# Wait for completion
docker logs -f ollama
```

---

## 📊 Port Reference

| Port | Service | URL |
|------|---------|-----|
| 3000 | Frontend | http://localhost:3000 |
| 8000 | API Gateway | http://localhost:8000 |
| 8003 | Reason Agent | http://localhost:8003 |
| 8004 | Risk Agent | http://localhost:8004 |
| 8005 | Decision Agent | http://localhost:8005 |
| 8007 | Extract Agent | http://localhost:8007 |
| 8008 | Verify Agent | http://localhost:8008 |
| 8010 | Orchestration | http://localhost:8010 |
| 8020 | MCP Server | http://localhost:8020 |
| 11434 | Ollama | http://localhost:11434 |

---

## 📚 Full Documentation

- **Installation**: See `INSTALLATION.md` for detailed setup
- **Architecture**: See `ARCHITECTURE.md` for system design

---

## ✅ System Requirements

| Component | Minimum |
|-----------|---------|
| CPU | 4 cores |
| RAM | 16 GB |
| Disk | 50 GB |
| OS | Linux/macOS/Windows |

---

## 🆘 Need Help?

1. Check service logs: `docker-compose logs <service>`
2. Verify health: `curl http://localhost:8000/health`
3. See troubleshooting in `INSTALLATION.md`
4. Check `docker-compose ps` for service status

---

**Last Updated**: April 7, 2026
