"""
Mock PAN Validation API Endpoint for Verify Agent
FastAPI endpoints that use mock_validation_api.py for testing
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
from mock_validation_api import MockPANValidator, validate_pan_mock, get_mock_test_cases

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize validator
validator = MockPANValidator()

# Pydantic models for request/response
class PANValidationRequest(BaseModel):
    """Request model for PAN validation"""
    pan_number: str
    name: Optional[str] = None
    father_name: Optional[str] = None
    dob: Optional[str] = None

class BatchValidationRequest(BaseModel):
    """Request model for batch PAN validation"""
    pan_list: List[str]

class MockValidationResponse(BaseModel):
    """Response model for validation"""
    pan_number: str
    name: Optional[str]
    status: str
    confidence: float
    details: dict
    timestamp: str
    is_mock: bool


# Create FastAPI app
app = FastAPI(
    title="Mock PAN Validation API",
    description="Mock validation API for testing PAN verification without external API calls",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mock-pan-validator",
        "is_mock": True
    }


@app.post("/validate-pan")
async def validate_pan_endpoint(request: PANValidationRequest):
    """
    Validate a PAN using mock pre-defined responses
    
    Example request:
    ```json
    {
        "pan_number": "CYMPB5839A",
        "name": "BORUGULA SURESH",
        "dob": "06/03/1992"
    }
    ```
    """
    try:
        logger.info(f"Mock validating PAN: {request.pan_number}")
        
        result = validator.validate_pan(
            pan_number=request.pan_number,
            name=request.name,
            dob=request.dob
        )
        
        logger.info(f"Validation result: {result['status']}")
        return result
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/batch-validate")
async def batch_validate_endpoint(request: BatchValidationRequest):
    """
    Validate multiple PANs in batch
    
    Example request:
    ```json
    {
        "pan_list": ["CYMPB5839A", "SAMPLE123X", "ABCDE1234F"]
    }
    ```
    """
    try:
        logger.info(f"Batch validating {len(request.pan_list)} PANs")
        
        result = validator.batch_validate_pans(request.pan_list)
        
        logger.info(f"Batch validation complete: {result['summary']}")
        return result
    except Exception as e:
        logger.error(f"Batch validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/test-cases")
async def get_test_cases_endpoint():
    """
    Get all available test cases for mock validation
    
    Returns a list of PAN numbers that have pre-defined responses
    """
    try:
        test_cases = validator.get_test_cases()
        
        return {
            "total_test_cases": len(test_cases),
            "test_cases": test_cases,
            "description": "These PAN numbers have pre-defined mock responses. Use them for testing.",
            "examples": {
                "valid_pan": "CYMPB5839A (Status: APPROVED)",
                "sample_pan": "SAMPLE123X (Status: REJECTED - Sample/Watermarked)",
                "invalid_format": "INVALID123 (Status: REJECTED - Invalid Format)",
                "photocopy": "PHOTOCOPY01 (Status: REJECTED - Photocopy)",
                "expired": "EXPIRY123A (Status: REJECTED - Expired)",
                "warning": "LOWQUAL22E (Status: WARNING - Low Quality)"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching test cases: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/validate-pan-simple")
async def validate_pan_simple(pan_number: str, name: Optional[str] = None):
    """
    Simple validation endpoint (query parameters)
    
    Example:
    `/validate-pan-simple?pan_number=CYMPB5839A&name=BORUGULA%20SURESH`
    """
    try:
        logger.info(f"Simple validation for: {pan_number}")
        
        result = validator.validate_pan(pan_number=pan_number, name=name)
        return result
    except Exception as e:
        logger.error(f"Simple validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/test-validate/{pan_number}")
async def test_validate_path(pan_number: str):
    """
    Direct path-based validation endpoint
    
    Example:
    `/test-validate/CYMPB5839A`
    """
    try:
        result = validator.validate_pan(pan_number=pan_number)
        return result
    except Exception as e:
        logger.error(f"Path validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/docs-mock")
async def mock_api_documentation():
    """
    Documentation for mock validation API
    """
    return {
        "title": "Mock PAN Validation API",
        "description": "Pre-defined mock responses for testing PAN verification",
        "endpoints": {
            "/validate-pan": {
                "method": "POST",
                "description": "Validate a single PAN",
                "request": {
                    "pan_number": "string (required)",
                    "name": "string (optional)",
                    "dob": "string (optional)"
                }
            },
            "/batch-validate": {
                "method": "POST",
                "description": "Validate multiple PANs",
                "request": {
                    "pan_list": ["list of PAN numbers"]
                }
            },
            "/test-cases": {
                "method": "GET",
                "description": "Get all available test cases"
            },
            "/validate-pan-simple": {
                "method": "POST",
                "description": "Simple validation with query parameters",
                "query_params": {
                    "pan_number": "string (required)",
                    "name": "string (optional)"
                }
            },
            "/test-validate/{pan_number}": {
                "method": "GET",
                "description": "Direct path-based validation"
            }
        },
        "test_cases_summary": {
            "CYMPB5839A": "APPROVED - Valid PAN with all fields",
            "ABCDE1234F": "APPROVED - Generic valid PAN",
            "SAMPLE123X": "REJECTED - Watermarked/Sample document",
            "INVALID123": "REJECTED - Invalid format",
            "PHOTOCOPY01": "REJECTED - Photocopy detected",
            "EXPIRY123A": "REJECTED - Document expired",
            "NOSIGN123C": "REJECTED - Signature missing",
            "NOPHOTO12D": "REJECTED - Photo missing",
            "LOWQUAL22E": "WARNING - Low quality but readable"
        },
        "notes": [
            "This is a MOCK API for development and testing",
            "Use pre-defined test cases for consistent results",
            "For unknown PANs, format validation is performed",
            "Returns is_mock: true in all responses"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
