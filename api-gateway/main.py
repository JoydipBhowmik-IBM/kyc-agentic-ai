from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import os
from datetime import datetime

# Set logging level from environment, default to WARNING to reduce noise
log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.WARNING))

# Suppress ChromaDB telemetry noisy logs
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)
logging.getLogger('chromadb').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(title="KYC API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ORCHESTRATION_SERVICE_URL = os.getenv("ORCHESTRATION_SERVICE_URL", "http://orchestration-service:8000")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        response = requests.get(f"{ORCHESTRATION_SERVICE_URL}/health", timeout=5)
        return {"status": "healthy", "orchestration_service": "connected"}
    except Exception as e:
        logger.warning(f"Orchestration service health check failed: {e}")
        return {"status": "degraded", "orchestration_service": "disconnected"}

@app.post("/kyc")
async def kyc(file: UploadFile = File(...)):
    """
    Process KYC request with uploaded document
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        logger.info(f"Processing KYC request for file: {file.filename}")
        start_time = datetime.now()

        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="File is empty")

        logger.info(f"File size: {len(content)} bytes")

        # Forward to orchestration service
        response = requests.post(
            f"{ORCHESTRATION_SERVICE_URL}/process",
            files={"file": (file.filename, content)},
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            logger.error(f"Orchestration service returned status {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Processing failed")

        result = response.json()
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"KYC processing completed in {elapsed_time}s")

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": elapsed_time,
            "result": result
        }

    except requests.exceptions.Timeout:
        logger.error("Request to orchestration service timed out")
        raise HTTPException(status_code=504, detail="Processing service timeout")
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to orchestration service")
        raise HTTPException(status_code=503, detail="Orchestration service unavailable")
    except Exception as e:
        logger.error(f"Error processing KYC request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
