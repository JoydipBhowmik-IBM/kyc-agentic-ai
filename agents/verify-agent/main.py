from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Verify Agent", version="1.0.0")

class VerificationRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    text: Optional[str] = None
    filename: Optional[str] = None
    status: Optional[str] = None

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

def validate_document_content(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate extracted document content"""
    validations = {
        "has_text": "text" in data and bool(data.get("text")),
        "has_filename": "filename" in data and bool(data.get("filename")),
        "text_length_sufficient": len(data.get("text", "")) > 10,
    }

    return validations

@app.post("/verify")
async def verify(data: Dict[str, Any]):
    """Verify extracted document information"""
    try:
        logger.info(f"Verifying document data")

        # Perform validation checks
        validations = validate_document_content(data)

        verified = all(validations.values())
        confidence_score = sum(validations.values()) / len(validations)

        result = {
            "status": "success",
            "verified": verified,
            "confidence_score": confidence_score,
            "validations": validations,
            "original_data": data,
            "timestamp": datetime.now().isoformat()
        }

        # Preserve critical KYC document type information from extract agent
        if "document_type" in data:
            result["document_type"] = data.get("document_type")
        if "confidence" in data:
            result["confidence"] = data.get("confidence")
        if "is_valid_kyc" in data:
            result["is_valid_kyc"] = data.get("is_valid_kyc")
        if "all_scores" in data:
            result["all_scores"] = data.get("all_scores")
        if "reason" in data:
            result["reason"] = data.get("reason")
        if "filename" in data:
            result["filename"] = data.get("filename")

        if verified:
            logger.info("Document verification passed")
        else:
            logger.warning(f"Document verification failed: {validations}")

        return result

    except Exception as e:
        logger.error(f"Error in verify: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")
