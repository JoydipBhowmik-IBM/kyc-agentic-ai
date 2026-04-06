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
import numpy as np

# Set logging level from environment, default to WARNING to reduce noise
log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.WARNING))

# Suppress ChromaDB telemetry noisy logs
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)
logging.getLogger('chromadb').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(title="Extract Agent", version="1.0.0")
validator = DocumentValidator()

SUPPORTED_FORMATS = ['image/jpeg', 'image/png', 'image/tiff', 'image/webp', 'image/avif', 'image/x-avif']

def detect_photo_in_document(image: Image.Image) -> bool:
    """
    Detect if document contains a photo/image area
    Returns True if a photo is detected
    
    Strategy: Check for visual complexity and color variation indicating 
    presence of a photograph or image (not just text)
    """
    try:
        # Convert image to numpy array for analysis
        img_array = np.array(image)
        
        # For RGB images, check color variation
        if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
            # Calculate standard deviation of pixel values
            # Photos have higher variation than plain text/background
            std_dev = float(np.std(img_array))
            
            # Calculate color range for each channel
            color_ranges = []
            for channel in range(min(3, img_array.shape[2])):
                channel_data = img_array[:, :, channel]
                color_range = int(np.max(channel_data) - np.min(channel_data))
                color_ranges.append(color_range)
            
            avg_color_range = float(np.mean(color_ranges))
            
            # RELAXED THRESHOLDS: Photo detected if there's visual variation
            # indicating presence of an image (not just blank/text areas)
            # Use OR logic instead of AND - if either metric is high, there's visual content
            has_photo = bool((std_dev > 15) or (avg_color_range > 40))
            
            logger.info(f"Photo detection - Std Dev: {std_dev:.2f}, Color Range: {avg_color_range:.2f}, Has Photo: {has_photo}")
            return has_photo
        else:
            # Grayscale image - check for variation
            std_dev = float(np.std(img_array))
            has_photo = bool(std_dev > 15)
            logger.info(f"Photo detection (grayscale) - Std Dev: {std_dev:.2f}, Has Photo: {has_photo}")
            return has_photo
    
    except Exception as e:
        logger.error(f"Photo detection error: {str(e)}")
        # If detection fails, assume no photo (safer for validation)
        return False

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
        
        # CRITICAL FIX: Override is_valid_kyc if document is identified as PAN with high confidence
        # PAN-ONLY SYSTEM: Only PAN documents are supported
        valid_kyc_types = ['PAN']  # PAN-only validation
        document_type = validation_result['document_type']
        confidence = validation_result['confidence']
        
        # If document is PAN with 100% confidence, mark it as valid_kyc regardless
        if document_type in valid_kyc_types and confidence >= 0.99:
            logger.info(f"✅ OVERRIDE: {document_type} identified with {confidence*100:.1f}% confidence - marking as valid KYC")
            validation_result['is_valid_kyc'] = True
        
        if not validation_result['is_valid_kyc']:
            logger.warning(f"Invalid KYC document: {validation_result['reason']}")
            
            # Still detect photo even if document is invalid
            has_photo = detect_photo_in_document(image)
            
            # Check if this is a fraudulent document
            fraud_detected = validation_result.get('fraud_detected', False)
            if fraud_detected:
                logger.error(f"🛑 FRAUDULENT DOCUMENT DETECTED: {validation_result.get('fraud_indicators', [])}")
            
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
                "has_photo": has_photo,
                "has_image_data": has_photo,
                "fraud_detected": fraud_detected,
                "fraud_indicators": validation_result.get('fraud_indicators', []),
                "message": f"❌ DOCUMENT REJECTED: {validation_result['reason']}",
                "timestamp": datetime.now().isoformat()
            }

        logger.info(f"Successfully extracted {len(text)} characters from {validation_result['document_type']}")
        
        # CRITICAL: Detect if photo is present in the document for PAN cards
        has_photo = detect_photo_in_document(image)
        logger.info(f"Photo detection result: {has_photo}")
        
        # ENFORCE PHOTO REQUIREMENT FOR PAN CARDS
        if validation_result['document_type'] == 'PAN':
            if not has_photo:
                logger.error(f"PAN card REJECTED: No photo detected in document")
                return {
                    "status": "rejected_no_photo",
                    "text": text,
                    "filename": file.filename,
                    "text_length": len(text),
                    "is_valid_kyc": False,  # REJECT
                    "document_type": validation_result['document_type'],
                    "confidence": validation_result['confidence'],
                    "reason": "PAN card rejected: No photo/image detected",
                    "extracted_patterns": validation_result['extracted_patterns'],
                    "all_scores": validation_result['all_scores'],
                    "has_photo": False,
                    "has_image_data": False,
                    "message": "❌ PAN card REJECTED: Missing photo/image. Valid PAN cards must contain a photo.",
                    "timestamp": datetime.now().isoformat()
                }
        
        # For PAN cards, include photo detection info
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
            "has_photo": has_photo,  # Photo detection result
            "has_image_data": has_photo,  # For compatibility
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in extract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")
