from fastapi import FastAPI, UploadFile, File, HTTPException
import pytesseract
from PIL import Image
import io
import logging
from datetime import datetime
from document_validator import DocumentValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Extract Agent", version="1.0.0")
validator = DocumentValidator()

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """Extract text from document image using OCR and validate document type"""
    try:
        logger.info(f"Extracting text from: {file.filename}")

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")

        # Convert to image
        try:
            image = Image.open(io.BytesIO(content))
        except Exception as e:
            logger.error(f"Failed to open image: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Extract text using Tesseract OCR
        text = pytesseract.image_to_string(image)

        if not text or text.strip() == "":
            logger.warning("No text extracted from image")
            return {
                "status": "error",
                "text": "",
                "message": "No readable text found in image",
                "is_valid_kyc": False,
                "document_type": "Unknown",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }

        # Validate document type
        validation_result = validator.validate_and_classify(text)
        
        logger.info(f"Document validation - Type: {validation_result['document_type']}, Valid KYC: {validation_result['is_valid_kyc']}")
        
        # CRITICAL FIX: Override is_valid_kyc if document is identified as valid KYC type with high confidence
        valid_kyc_types = ['PAN', 'Aadhar', 'Passport', 'Driving License', 'Voter ID', 'Bank Statement', 'Utility Bill']
        document_type = validation_result['document_type']
        confidence = validation_result['confidence']
        
        # If document is a valid KYC type with 100% confidence, mark it as valid_kyc regardless
        if document_type in valid_kyc_types and confidence >= 0.99:
            logger.info(f"✅ OVERRIDE: {document_type} identified with {confidence*100:.1f}% confidence - marking as valid KYC")
            validation_result['is_valid_kyc'] = True
        
        if not validation_result['is_valid_kyc']:
            logger.warning(f"Invalid KYC document: {validation_result['reason']}")
            return {
                "status": "invalid_document",
                "text": text,
                "filename": file.filename,
                "text_length": len(text),
                "is_valid_kyc": False,
                "document_type": validation_result['document_type'],
                "confidence": validation_result['confidence'],
                "reason": validation_result['reason'],
                "all_scores": validation_result['all_scores'],
                "message": f"This does not appear to be a valid KYC document. {validation_result['reason']}",
                "timestamp": datetime.now().isoformat()
            }

        logger.info(f"Successfully extracted {len(text)} characters from {validation_result['document_type']}")
        return {
            "status": "success",
            "text": text,
            "filename": file.filename,
            "text_length": len(text),
            "is_valid_kyc": True,
            "document_type": validation_result['document_type'],
            "confidence": validation_result['confidence'],
            "reason": validation_result['reason'],
            "extracted_patterns": validation_result['extracted_patterns'],
            "all_scores": validation_result['all_scores'],
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in extract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")
