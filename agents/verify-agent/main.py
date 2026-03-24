from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

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
    # Check if this is a valid KYC document from the extract agent
    is_valid_kyc = data.get("is_valid_kyc", False)
    
    validations = {
        "has_text": "text" in data and bool(data.get("text")),
        "is_valid_kyc": is_valid_kyc,  # Critical: Use the KYC validation from extract agent
        "text_length_sufficient": len(data.get("text", "")) > 10,
    }

    return validations

def cross_verify_with_sources(data: Dict[str, Any], sources: List[str]) -> Dict[str, Any]:
    """Perform cross-verification against multiple sources."""
    cross_verifications = {}
    for source in sources:
        # Simulate cross-verification logic
        cross_verifications[source] = True  # Replace with actual verification logic

    return cross_verifications

@app.post("/verify")
async def verify(data: Dict[str, Any]):
    """Verify extracted document information with multi-source cross-verification."""
    try:
        logger.info(f"Verifying document data")
        
        # DEBUG: Log incoming data
        logger.info(f"Verify Agent Received:")
        logger.info(f"  - is_valid_kyc: {data.get('is_valid_kyc')} (from extract agent)")
        logger.info(f"  - document_type: {data.get('document_type')}")
        logger.info(f"  - text length: {len(data.get('text', ''))}")
        
        # CRITICAL: If extract agent explicitly marked this as NOT a valid KYC document, reject
        # But only if is_valid_kyc is explicitly FALSE, not if it's missing
        if "is_valid_kyc" in data and data.get("is_valid_kyc") is False:
            logger.warning("Document explicitly failed KYC validation from extract agent - rejecting")
            result = {
                "status": "success",
                "verified": False,
                "confidence_score": 0.0,
                "validations": {"is_valid_kyc": False},
                "cross_verifications": {},
                "is_valid_kyc": False,  # CRITICAL: Must preserve for decision agent
                "original_data": data,
                "timestamp": datetime.now().isoformat()
            }
            # Preserve critical KYC document type information
            if "document_type" in data:
                result["document_type"] = data.get("document_type")
            if "confidence" in data:
                result["confidence"] = data.get("confidence")
            if "reason" in data:
                result["reason"] = data.get("reason")
            if "filename" in data:
                result["filename"] = data.get("filename")
            
            logger.warning(f"Document verification failed: {data.get('reason')}")
            return result

        # Perform validation checks
        validations = validate_document_content(data)
        
        logger.info(f"Validation checks completed:")
        logger.info(f"  - has_text: {validations.get('has_text')}")
        logger.info(f"  - is_valid_kyc: {validations.get('is_valid_kyc')}")
        logger.info(f"  - text_length_sufficient: {validations.get('text_length_sufficient')}")

        # Perform cross-verification
        sources = ["source1", "source2", "source3"]  # Replace with actual sources
        cross_verifications = cross_verify_with_sources(data, sources)

        # For valid KYC documents, we trust the extract agent's classification
        # Only require text to be present
        verified = validations["has_text"] and validations["is_valid_kyc"] and all(cross_verifications.values())
        confidence_score = (sum(validations.values()) + sum(cross_verifications.values())) / max(1, (len(validations) + len(cross_verifications)))

        result = {
            "status": "success",
            "verified": verified,
            "confidence_score": confidence_score,
            "validations": validations,
            "cross_verifications": cross_verifications,
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
            logger.info("✓ Document verification PASSED")
            logger.info(f"  - verified: {verified}")
            logger.info(f"  - is_valid_kyc: {result.get('is_valid_kyc')}")
        else:
            logger.warning(f"✗ Document verification FAILED: {validations}")
            logger.warning(f"  - verified: {verified}")
            logger.warning(f"  - is_valid_kyc: {result.get('is_valid_kyc')}")

        return result

    except Exception as e:
        logger.error(f"Error in verify: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")
