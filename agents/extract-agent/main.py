from fastapi import FastAPI, UploadFile, File, HTTPException
import pytesseract
from PIL import Image
import io
import logging
from datetime import datetime
from document_validator import DocumentValidator
import mimetypes
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Extract Agent", version="1.0.0")
validator = DocumentValidator()

SUPPORTED_FORMATS = ['image/jpeg', 'image/png', 'image/tiff', 'image/webp', 'image/avif', 'image/x-avif']

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

def convert_avif_to_png(content: bytes) -> bytes:
    """Convert AVIF image to PNG using ImageMagick"""
    try:
        # Save AVIF temporarily
        temp_avif = "/tmp/temp_image.avif"
        temp_png = "/tmp/temp_image.png"
        
        with open(temp_avif, 'wb') as f:
            f.write(content)
        
        # Convert using ImageMagick
        result = subprocess.run(
            ['convert', temp_avif, temp_png],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            logger.error(f"ImageMagick conversion failed: {result.stderr.decode()}")
            raise Exception("ImageMagick conversion failed")
        
        # Read converted PNG
        with open(temp_png, 'rb') as f:
            png_content = f.read()
        
        # Cleanup
        os.remove(temp_avif)
        os.remove(temp_png)
        
        logger.info("Successfully converted AVIF to PNG")
        return png_content
    except Exception as e:
        logger.error(f"AVIF conversion error: {str(e)}")
        raise

def convert_image_to_rgb(image: Image.Image) -> Image.Image:
    """Convert image to RGB if needed for OCR"""
    if image.mode in ('RGBA', 'LA', 'P'):
        # Convert to RGB
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        return rgb_image
    elif image.mode != 'RGB':
        return image.convert('RGB')
    return image

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """Extract text from document image using OCR and validate document type"""
    try:
        logger.info(f"Extracting text from: {file.filename}")

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")

        # Convert AVIF to PNG if needed
        if file.filename.lower().endswith('.avif'):
            logger.info("AVIF file detected, converting to PNG...")
            try:
                content = convert_avif_to_png(content)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"AVIF conversion failed: {str(e)}")

        # Convert to image with better error handling
        try:
            image = Image.open(io.BytesIO(content))
            # Load image data to test if it's valid
            image.load()
            # Convert to RGB if needed
            image = convert_image_to_rgb(image)
            logger.info(f"Successfully opened image: {image.format} {image.size} {image.mode}")
        except Exception as e:
            logger.error(f"Failed to open image: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

        # Extract text using Tesseract OCR with configuration
        try:
            # Use configuration for better text extraction
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # If no text found, try alternative PSM
            if not text or text.strip() == "":
                logger.warning("First OCR attempt failed, trying alternative PSM...")
                text = pytesseract.image_to_string(image, config=r'--psm 3')
            
            logger.info(f"OCR extracted {len(text)} characters")
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OCR processing error: {str(e)}")

        if not text or text.strip() == "":
            logger.warning("No text extracted from image")
            return {
                "status": "error",
                "text": "",
                "message": "No readable text found in image. The image quality might be too low or the document might not contain extractable text.",
                "is_valid_kyc": False,
                "document_type": "Unknown",
                "confidence": 0.0,
                "filename": file.filename,
                "timestamp": datetime.now().isoformat()
            }

        # Validate document type
        validation_result = validator.validate_and_classify(text)
        
        logger.info(f"Document validation - Type: {validation_result['document_type']}, Valid KYC: {validation_result['is_valid_kyc']}")
        
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
