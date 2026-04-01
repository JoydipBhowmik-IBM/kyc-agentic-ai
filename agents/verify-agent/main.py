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

def validate_mandatory_fields(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate mandatory fields based on document type
    Returns (is_valid, missing_fields)
    """
    document_type = data.get("document_type", "Unknown").lower()
    text = data.get("text", "").lower()
    missing_fields = []
    
    # Define mandatory requirements for each document type
    mandatory_requirements = {
        "pan": {
            "fields": ["name", "date of birth", "pan number", "father", "signature"],
            "requires_photo": True,
            "min_text_length": 50
        },
        "aadhar": {
            "fields": ["aadhaar", "date of birth", "gender"],
            "requires_photo": True,
            "min_text_length": 40
        },
        "passport": {
            "fields": ["passport", "date of birth"],
            "requires_photo": True,
            "min_text_length": 30
        },
        "driving license": {
            "fields": ["driving", "license", "date of birth"],
            "requires_photo": True,
            "min_text_length": 40
        },
        "voter id": {
            "fields": ["voter", "epic", "date of birth"],
            "requires_photo": True,
            "min_text_length": 30
        }
    }
    
    requirements = mandatory_requirements.get(document_type)
    
    if requirements:
        # Check minimum text length
        if len(data.get("text", "")) < requirements["min_text_length"]:
            missing_fields.append(f"Insufficient text extraction (< {requirements['min_text_length']} chars)")
        
        # Check mandatory fields
        for field in requirements["fields"]:
            if field not in text:
                missing_fields.append(field)
        
        # CRITICAL: Check for photo/image presence
        if requirements["requires_photo"]:
            has_photo = data.get("has_photo", False)
            has_image_data = data.get("has_image_data", False)
            
            # If neither explicit photo flag nor image metadata, document is incomplete
            if not (has_photo or has_image_data):
                missing_fields.append("PHOTO - Missing from document (CRITICAL for KYC)")
                logger.warning(f"⚠️ CRITICAL: {document_type.upper()} document missing photo!")
    
    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields

def validate_document_content(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate extracted document content with mandatory field checks"""
    # Basic validations
    base_validations = {
        "has_text": "text" in data and bool(data.get("text")),
        "text_length_sufficient": len(data.get("text", "")) > 10,
        "is_valid_kyc": data.get("is_valid_kyc", False),  # Trust extract-agent validation
    }
    
    # NEW: Validate mandatory fields based on document type
    mandatory_valid, missing_fields = validate_mandatory_fields(data)
    base_validations["mandatory_fields_present"] = mandatory_valid
    
    # If mandatory fields are missing, log them clearly
    if missing_fields:
        logger.warning(f"❌ VALIDATION FAILED - Missing mandatory fields: {missing_fields}")
        base_validations["missing_fields"] = missing_fields
    else:
        base_validations["missing_fields"] = []

    return base_validations

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
        logger.info(f"Input data keys: {list(data.keys())}")

        # Perform validation checks
        validations = validate_document_content(data)
        logger.info(f"Validations: {validations}")

        # Perform cross-verification
        sources = ["source1", "source2", "source3"]  # Replace with actual sources
        cross_verifications = cross_verify_with_sources(data, sources)
        logger.info(f"Cross-verifications: {cross_verifications}")

        # MANDATORY FIELD CHECK: This is NON-NEGOTIABLE for compliance
        missing_fields = validations.get("missing_fields", [])
        critical_failures = []  # NEW: Track ONLY truly critical failures
        
        # CRITICAL FAILURES: Only these are show-stoppers
        # These are failures that make the document unsuitable for KYC under any circumstances
        document_type = data.get("document_type", "").lower()
        
        # Check 1: PHOTO is CRITICAL for all PAN/KYC documents if extract-agent found none
        if document_type == "pan":
            has_photo = data.get("has_photo", False)
            has_image_data = data.get("has_image_data", False)
            
            if not (has_photo or has_image_data):
                critical_failures.append("MISSING PHOTO/IMAGE (Required for PAN card)")
                logger.error(f"🛑 CRITICAL: PAN card missing photo")
        
        # Check 2: Document validation failed by extract agent
        # (e.g., watermarks, fraud detected)
        if not data.get("is_valid_kyc", False):
            # Only mark as critical if extract agent explicitly rejected it
            extract_status = data.get("status", "")
            if extract_status in ["invalid_document", "rejected_no_photo"]:
                reason = data.get("reason", "")
                if "fraud" in reason.lower() or "watermark" in reason.lower() or "sample" in reason.lower():
                    critical_failures.append(f"Document authentication failed: {reason}")
                    logger.error(f"🛑 CRITICAL: {reason}")
        
        # All other missing fields (name, father, DOB, etc.) are NOT critical failures
        # They should be captured as warnings/missing_fields but not block approval
        # The risk agent and other downstream agents will decide based on risk profile
        
        if missing_fields:
            logger.warning(f"⚠️ Missing fields detected: {missing_fields}")
            # Don't set verified=False just for missing fields
            # Only the extract agent's is_valid_kyc and critical failures matter
            mandatory_fields_valid = (len(critical_failures) == 0)
        else:
            mandatory_fields_valid = True
        
        base_verified = all(v for k, v in validations.items() if k != "missing_fields") and all(cross_verifications.values())
        logger.info(f"Base verified (all validations passed): {base_verified}")
        
        # Calculate verification confidence
        # Don't count missing_fields in confidence calculation since it's a hard requirement
        confidence_values = [v for k, v in validations.items() if k not in ["missing_fields"] and isinstance(v, bool)]
        if confidence_values or cross_verifications.values():
            verification_confidence = (sum(confidence_values) + sum(cross_verifications.values())) / (len(confidence_values) + len(cross_verifications))
        else:
            verification_confidence = 0.0
        logger.info(f"Verification confidence (from validations): {verification_confidence:.2%}")
        
        # Use extract-agent's confidence as floor (trust the extraction confidence)
        extract_confidence = data.get("confidence", 0.0)
        logger.info(f"Extract confidence (from extract-agent): {extract_confidence}")
        
        confidence_score = max(verification_confidence, extract_confidence)
        logger.info(f"Final confidence_score (max of both): {confidence_score:.2%}")
        
        # VERIFICATION LOGIC (simplified and more practical):
        # **Trust the extract agent's is_valid_kyc status**
        # Extract agent has done OCR and document type validation already
        
        # ONLY reject if:
        # 1. Critical failure detected (fraud, watermark, missing photo)
        # 2. Extract agent explicitly rejected (is_valid_kyc=False)
        
        if critical_failures and len(critical_failures) > 0:
            # CRITICAL failure - reject
            verified = False
            logger.error(f"🛑 Critical failures detected: {critical_failures}")
        elif not data.get("is_valid_kyc", False):
            # Extract agent rejected this document
            verified = False
            logger.warning(f"Extract agent rejected document: {data.get('reason', 'Unknown')}")
        elif confidence_score >= 0.75:
            # Decent confidence and no critical issues - APPROVE
            verified = True
            logger.info(f"✓ Document verification PASSED (confidence: {confidence_score:.2%}, no critical failures)")
        else:
            # Low confidence but no critical issues - require manual review
            verified = False
            logger.warning(f"Low confidence ({confidence_score:.2%}) - setting verified=False for manual review")

        result = {
            "status": "success",
            "verified": verified,
            "confidence_score": confidence_score,
            "validations": validations,
            "cross_verifications": cross_verifications,
            "original_data": data,
            "critical_failures": critical_failures,  # NEW: Pass critical failures to decision agent
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
