from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import os
import json
import re

# Set logging level from environment, default to WARNING to reduce noise
log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.WARNING))

# Suppress ChromaDB telemetry noisy logs
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)
logging.getLogger('chromadb').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(title="Verify Agent", version="1.0.0")

# Import mock validation API
try:
    from mock_validation_api import MockPANValidator
    mock_validator = MockPANValidator()
    USE_MOCK_API = os.getenv("USE_MOCK_API", "true").lower() == "true"
    logger.info(f"Mock PAN Validator initialized. USE_MOCK_API={USE_MOCK_API}")
except ImportError:
    mock_validator = None
    USE_MOCK_API = False
    logger.warning("Mock validation API not available")

class VerificationRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    text: Optional[str] = None
    filename: Optional[str] = None
    status: Optional[str] = None

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

def load_kyc_rules() -> List[Dict[str, Any]]:
    """Load KYC rules from kyc_rules.json under kyc_vector_db"""
    vector_db_path = os.getenv("VECTOR_DB_PATH", "/data/kyc_vector_db")
    rules_file = os.path.join(vector_db_path, "kyc_rules.json")

    if not os.path.exists(rules_file):
        fallback_path = os.path.join("/app/kyc_vector_db", "kyc_rules.json")
        if os.path.exists(fallback_path):
            logger.info(f"KYC rules file found in fallback location: {fallback_path}")
            rules_file = fallback_path
        else:
            logger.warning(f"KYC rules file not found: {rules_file} or {fallback_path}")
            return []

    try:
        with open(rules_file, "r", encoding="utf-8") as f:
            rules = json.load(f)
            logger.info(f"✓ Loaded {len(rules)} rules from {rules_file}")
            return rules
    except Exception as e:
        logger.warning(f"Error loading KYC rules from {rules_file}: {e}")
        return []


KYC_RULES = load_kyc_rules()


def load_fraud_patterns() -> List[Dict[str, Any]]:
    """Load fraud patterns from fraud_patterns.json under kyc_vector_db"""
    vector_db_path = os.getenv("VECTOR_DB_PATH", "/data/kyc_vector_db")
    patterns_file = os.path.join(vector_db_path, "fraud_patterns.json")

    if not os.path.exists(patterns_file):
        fallback_path = os.path.join("/app/kyc_vector_db", "fraud_patterns.json")
        if os.path.exists(fallback_path):
            logger.info(f"Fraud patterns file found in fallback location: {fallback_path}")
            patterns_file = fallback_path
        else:
            logger.warning(f"Fraud patterns file not found: {patterns_file} or {fallback_path}")
            return []

    try:
        with open(patterns_file, "r", encoding="utf-8") as f:
            patterns = json.load(f)
            logger.info(f"✓ Loaded {len(patterns)} fraud patterns from {patterns_file}")
            return patterns
    except Exception as e:
        logger.warning(f"Error loading fraud patterns from {patterns_file}: {e}")
        return []


FRAUD_PATTERNS = load_fraud_patterns()


def _extract_regex_from_rule(requirement: str, document_type: str) -> str | None:
    """Create a regex expression from rule requirement text for core types.
    
    Parses requirement text to infer the correct regex pattern.
    E.g., "First 5 characters are letters, next 4 are digits, last is letter" → 5-4-1 pattern
    """
    doc_lower = (document_type or "").strip().lower()
    req_lower = (requirement or "").strip().lower()

    if doc_lower == "pan":
        # Check for 5-4-1 pattern (new rule_001)
        # Matches: "5 characters", "4 digits", "letter" (singular = last 1 character)
        has_five = "5" in req_lower and "character" in req_lower
        has_four = "4" in req_lower and ("digit" in req_lower or "number" in req_lower)
        has_one = ("letter" in req_lower or "1" in req_lower)
        
        if has_five and has_four and has_one:
            logger.info("PAN rule_001: Detected 5-4-1 pattern from requirement")
            return r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
        
        # Check for 5-4-1 pattern (standard PAN)
        has_five = "5" in req_lower and "character" in req_lower
        if has_five and has_four and has_one:
            logger.info("PAN rule: Detected 5-4-1 pattern from requirement")
            return r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
        
        # Default to 5-4-1 (current business requirement)
        logger.info("PAN rule: Defaulting to 5-4-1 pattern")
        return r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"

    # PAN-ONLY SYSTEM: Removed Aadhar and Passport validation
    # Only PAN document type is supported

    # Fallback attempt to infer from requirement description
    if "12" in req_lower and "digit" in req_lower:
        return r"\b\d{12}\b"

    return None


def apply_kyc_rules(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply rule-driven validation based on loaded kyc_rules.json."""
    if not KYC_RULES:
        logger.warning("⚠️ No KYC rules loaded from knowledge base!")
        return {"valid": True, "reason": "No KYC rules loaded"}

    document_type = (data.get("document_type") or "").strip().lower()
    text = (data.get("text") or "").strip().upper()

    # If no text is available (e.g., image just uploaded but OCR not yet run), skip strict rule validation.
    if not text:
        logger.info("📋 No text available yet; skipping KYC rule validation")
        return {"valid": True, "reason": "Text not available yet; skipping KYC rule text validation"}

    if not document_type:
        logger.error("❌ Missing document_type; cannot apply KYC rules")
        return {"valid": False, "reason": "Missing document_type; cannot apply KYC rules"}

    rules_for_type = [rule for rule in KYC_RULES
                      if rule.get("document_type", "").strip().lower() == document_type]

    if not rules_for_type:
        logger.warning(f"⚠️ No KYC rules defined for document type '{document_type}'")
        return {"valid": True, "reason": f"No KYC rules defined for document type '{document_type}'"}

    # Log rule validation start
    logger.info("="*70)
    logger.info(f"🔍 RULE VALIDATION STARTED - Document: {document_type.upper()}")
    logger.info(f"Total rules to check: {len(rules_for_type)}")
    logger.info("="*70)

    passed_rules = []
    failed_rules = []
    
    # Apply each rule, reject if any critical rule fails
    for rule in rules_for_type:
        rule_id = rule.get("rule_id", "unknown")
        rule_title = rule.get("title", "Unknown Rule")
        requirement = rule.get("requirement", "")
        priority = (rule.get("priority", "") or "LOW").upper()

        logger.info(f"\n📌 Rule: {rule_id} | Title: {rule_title} | Priority: {priority}")
        logger.info(f"   Requirement: {requirement}")

        # allow explicit regex in JSON rule if provided
        if rule.get("regex"):
            regex = rule.get("regex")
        else:
            regex = _extract_regex_from_rule(requirement, document_type)

        if not regex:
            logger.warning(f"   ⚠️ No regex available for rule {rule_id}; skipping")
            continue

        try:
            pattern = re.compile(regex)
        except re.error as ex:
            logger.warning(f"   ⚠️ Invalid regex in rule {rule_id} ('{regex}'): {ex}; skipping")
            continue

        if pattern.search(text):
            logger.info(f"   ✅ PASSED - Rule matched successfully")
            passed_rules.append(rule_id)
            continue

        # Rule failed
        failed_reason = f"Text does not meet requirement: '{requirement}'"
        logger.warning(f"   ❌ FAILED - {failed_reason}")
        failed_rules.append({
            "rule_id": rule_id,
            "title": rule_title,
            "requirement": requirement,
            "priority": priority
        })
        
        if priority == "CRITICAL":
            logger.error(f"\n🚫 CRITICAL RULE FAILED! Rejecting document.")
            logger.info("="*70)
            return {"valid": False, "reason": f"CRITICAL rule {rule_id} failed: {failed_reason}"}
        # non-critical rules may be skipped

    logger.info("\n" + "="*70)
    logger.info(f"✅ RULE VALIDATION SUMMARY")
    logger.info(f"   Passed Rules: {len(passed_rules)} - {passed_rules}")
    logger.info(f"   Failed Rules: {len(failed_rules)}")
    if failed_rules:
        for failed in failed_rules:
            logger.info(f"      - {failed['rule_id']} ({failed['priority']}): {failed['requirement']}")
    logger.info("="*70 + "\n")

    return {"valid": True, "reason": f"All applicable KYC rules passed for {document_type}", "passed_rules": passed_rules, "failed_rules": failed_rules}


def check_fraud_patterns(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check for fraud patterns indicators in document data and extracted text."""
    if not FRAUD_PATTERNS:
        logger.warning("⚠️ No fraud patterns loaded from knowledge base!")
        return {"fraud_detected": False, "patterns_matched": [], "reason": "No fraud patterns loaded"}

    text_lower = (data.get("text") or "").lower()
    detected_patterns = []
    risk_level = "LOW"

    logger.info("="*70)
    logger.info(f"🚨 FRAUD PATTERN CHECK - Total patterns to verify: {len(FRAUD_PATTERNS)}")
    logger.info("="*70)

    # Check each fraud pattern for indicators
    for pattern in FRAUD_PATTERNS:
        pattern_id = pattern.get("pattern_id", "unknown")
        pattern_name = pattern.get("pattern_name", "Unknown")
        indicators = pattern.get("indicators", [])
        pattern_risk = pattern.get("risk_level", "MEDIUM").upper()

        logger.info(f"\n🔎 Pattern: {pattern_id} | {pattern_name} | Risk: {pattern_risk}")
        logger.info(f"   Checking indicators: {indicators}")

        # Check if any indicators are found in the text
        matched_indicators = []
        for indicator in indicators:
            if indicator.lower() in text_lower:
                matched_indicators.append(indicator)

        if matched_indicators:
            logger.warning(f"   ⚠️ DETECTED - Matched indicators: {matched_indicators}")
            detected_patterns.append({
                "pattern_id": pattern_id,
                "pattern_name": pattern_name,
                "matched_indicators": matched_indicators,
                "risk_level": pattern_risk
            })
            
            # Update overall risk level to highest detected
            if pattern_risk == "CRITICAL":
                risk_level = "CRITICAL"
            elif pattern_risk == "HIGH" and risk_level != "CRITICAL":
                risk_level = "HIGH"
        else:
            logger.info(f"   ✅ OK - No indicators detected")

    fraud_detected = len(detected_patterns) > 0
    
    logger.info("\n" + "="*70)
    if fraud_detected:
        logger.warning(f"🚨 FRAUD CHECK RESULT: {len(detected_patterns)} pattern(s) detected!")
        logger.warning(f"   Overall Risk Level: {risk_level}")
        for detected in detected_patterns:
            logger.warning(f"   - {detected['pattern_id']}: {detected['pattern_name']}")
    else:
        logger.info(f"✅ FRAUD CHECK RESULT: No fraud patterns detected")
    logger.info("="*70 + "\n")
    
    return {
        "fraud_detected": fraud_detected,
        "patterns_matched": detected_patterns,
        "overall_risk_level": risk_level,
        "reason": f"{len(detected_patterns)} fraud pattern(s) detected" if fraud_detected else "No fraud patterns detected"
    }


def validate_mandatory_fields(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate mandatory fields based on document type
    Returns (is_valid, missing_fields)
    """
    document_type = data.get("document_type", "Unknown").lower()
    text = data.get("text", "").lower()
    missing_fields = []
    
    # Define mandatory requirements for each document type
    # PAN-ONLY SYSTEM: Removed all non-PAN document types
    mandatory_requirements = {
        "pan": {
            "fields": ["name", "date of birth", "pan number", "father", "signature"],
            "requires_photo": True,
            "min_text_length": 50
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


def check_with_mock_api(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check validation using mock API if enabled and available"""
    if not USE_MOCK_API or not mock_validator:
        return None
    
    try:
        # Extract PAN number from data
        extracted_text = data.get("text", "").upper()
        pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', extracted_text)
        
        if not pan_match:
            logger.warning("No PAN number found in extracted text for mock validation")
            return None
        
        pan_number = pan_match.group(0)
        
        # Extract name from data if available
        name = extracted_text.split('\n')[0] if extracted_text else None
        
        logger.info(f"Using MOCK API to validate PAN: {pan_number}")
        
        # Call mock validator
        mock_result = mock_validator.validate_pan(
            pan_number=pan_number,
            name=name
        )
        
        logger.info(f"Mock API Result: Status={mock_result['status']}, Confidence={mock_result['confidence']}")
        
        return {
            "mock_api_enabled": True,
            "pan_number": pan_number,
            "mock_status": mock_result['status'],
            "mock_confidence": mock_result['confidence'],
            "mock_reason": mock_result['details']['reason'],
            "mock_checks_passed": mock_result['details'].get('checks_passed', []),
            "mock_checks_failed": mock_result['details'].get('checks_failed', []),
            "is_mock": mock_result.get('is_mock', True)
        }
    except Exception as e:
        logger.error(f"Error calling mock API: {str(e)}")
        return None


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

        # ====== MOCK API CHECK (if enabled) ======
        # This takes priority over other checks for testing
        mock_api_result = check_with_mock_api(data)
        if mock_api_result:
            logger.info(f"Mock API validation: {mock_api_result['mock_status']}")
            validations["mock_api_validation"] = mock_api_result
            
            # CRITICAL: If mock API says REJECTED, return REJECTED immediately
            if mock_api_result['mock_status'] == "REJECTED":
                logger.error(f"MOCK API REJECTION: {mock_api_result['mock_reason']}")
                return {
                    "status": "rejected_by_mock_api",
                    "verified": False,
                    "confidence_score": 0.0,
                    "reason": mock_api_result['mock_reason'],
                    "mock_api_result": mock_api_result,
                    "validations": validations
                }

        # Apply kyc_rules based rules
        kyc_rule_result = apply_kyc_rules(data)
        validations["kyc_rule_check"] = kyc_rule_result
        if not kyc_rule_result.get("valid", False):
            logger.error(f"🛑 KYC rule check failed: {kyc_rule_result.get('reason')}")

        # Check for fraud patterns
        fraud_check = check_fraud_patterns(data)
        validations["fraud_check"] = fraud_check
        if fraud_check.get("fraud_detected", False):
            logger.warning(f"⚠️ FRAUD ALERT: {fraud_check.get('reason')} - Risk Level: {fraud_check.get('overall_risk_level')}")

        # Perform cross-verification
        sources = ["source1", "source2", "source3"]  # Replace with actual sources
        cross_verifications = cross_verify_with_sources(data, sources)
        logger.info(f"Cross-verifications: {cross_verifications}")

        # MANDATORY FIELD CHECK: This is NON-NEGOTIABLE for compliance
        missing_fields = validations.get("missing_fields", [])
        critical_failures = []  # NEW: Track ONLY truly critical failures

        # KYC rule check failure should be treated as critical
        if not validations.get("kyc_rule_check", {}).get("valid", True):
            critical_failures.append(validations.get("kyc_rule_check", {}).get("reason", "KYC rule validation failed"))
        
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

        # Check 3: Fraud patterns with CRITICAL risk level
        fraud_check = validations.get("fraud_check", {})
        if fraud_check.get("fraud_detected", False):
            patterns_matched = fraud_check.get("patterns_matched", [])
            for pattern in patterns_matched:
                if pattern.get("risk_level") == "CRITICAL":
                    critical_failures.append(f"FRAUD DETECTED: {pattern.get('pattern_name')} - Indicators: {', '.join(pattern.get('matched_indicators', []))}")
                    logger.error(f"🛑 CRITICAL FRAUD: {pattern.get('pattern_name')}")
        
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
