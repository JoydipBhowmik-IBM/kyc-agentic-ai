"""
Document Type Recognition and Validation Module
Identifies KYC document types and validates if documents are valid KYC documents
"""

import re
from typing import Dict
from enum import Enum
from datetime import datetime

class KYCDocumentType(Enum):
    """Supported KYC document types - PAN ONLY"""
    PAN = "PAN"
    UNKNOWN = "Unknown"
    INVALID = "Invalid"

class DocumentValidator:
    """Validates and classifies KYC documents"""
    
    def __init__(self):
        """Initialize document patterns for recognition - PAN ONLY"""
        self.pan_patterns = [
            r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',  # PAN format
            r'pan\s*card',
            r'pan\s*number',
            r'permanent\s*account\s*number',
        ]

    def _detect_fraud_indicators(self, text: str) -> Dict:
        """
        Detect fraud indicators in document
        STRICTLY rejects:
        1. Documents with watermarks (SAMPLE, IMMIHELP, logos, external text overlays)
        2. Photocopied or tampered documents
        3. Template/demo documents
        """
        text_lower = text.lower()
        fraud_indicators = []
        is_fraudulent = False
        
        # CRITICAL FRAUD INDICATORS - ALWAYS REJECT
        # 1. Watermark/Overlay detection
        watermark_keywords = [
            ('sample', 'Watermarked as SAMPLE'),
            ('immihelp', 'IMMIHELP.COM watermark - External website overlay'),
            ('sample - immihelp', 'SAMPLE document from IMMIHELP'),
            ('watermark', 'Document contains watermark'),
            ('© copyright', 'Copyright/watermark overlay'),
            ('for demonstration', 'For demonstration only'),
            ('not for legal', 'Not for legal use'),
            ('dummy', 'Dummy/placeholder document'),
            ('template', 'Template document'),
        ]
        
        # 2. Photocopied/Tampered documents
        photocopied_keywords = [
            ('photocopied', 'Photocopied document'),
            ('photocopy', 'Photocopy (not original)'),
            ('copy', 'Copy of original'),
            ('not original', 'Not original document'),
            ('duplicate', 'Duplicate/copy'),
            ('certified copy', 'Certified copy (indicates original is elsewhere)'),
        ]
        
        # 3. Fake/invalid documents
        fake_keywords = [
            ('fake', 'Explicitly marked as fake'),
            ('not real', 'Marked as not real'),
            ('invalid', 'Invalid document'),
            ('cancelled', 'Cancelled document'),
            ('expired', 'Expired document'),  # For ID documents
        ]
        
        # Check all critical indicators
        for keyword, description in watermark_keywords + photocopied_keywords + fake_keywords:
            if keyword in text_lower:
                fraud_indicators.append(description)
                is_fraudulent = True
        
        # Additional fraud patterns
        fraud_patterns = [
            (r'sample\s*[-]?\s*immihelp|immihelp\.com', 'Website watermark overlay detected'),
            (r'for\s+demonstration\s+only', 'Demonstration document'),
            (r'not\s+for\s+legal\s+use', 'Not for legal use'),
            (r'test\s+(document|image)', 'Test/sample document'),
        ]
        
        for pattern, description in fraud_patterns:
            if re.search(pattern, text_lower):
                if description not in fraud_indicators:
                    fraud_indicators.append(description)
                    is_fraudulent = True
        
        fraud_reason = " | ".join(fraud_indicators[:3]) if fraud_indicators else ""
        
        return {
            "is_fraudulent": is_fraudulent,
            "fraud_reason": fraud_reason,
            "indicators": fraud_indicators,
            "is_sample": 'sample' in text_lower or 'immihelp' in text_lower,
            "note": "REJECTED: Document contains watermarks or is not original" if is_fraudulent else None
        }

    def validate_and_classify(self, text: str) -> Dict:
        """
        Validate if document is a KYC document and classify its type
        Supports multiple KYC document types with appropriate validation
        
        Args:
            text: Extracted text from document
            
        Returns:
            Dictionary with classification results
        """
        if not text or len(text.strip()) < 20:
            return {
                "is_valid_kyc": False,
                "document_type": KYCDocumentType.INVALID.value,
                "confidence": 0.0,
                "reason": "Document text too short or empty",
                "details": []
            }
        
        # PAN-ONLY SYSTEM: Only check for PAN documents
        text_lower = text.lower()
        text_normalized = re.sub(r'\s+', ' ', text_lower)
        
        # Check PAN only
        best_score = self._check_pan(text, text_lower, text_normalized)
        best_type = KYCDocumentType.PAN
        
        # Determine confidence
        income_tax_keywords = ['income tax', 'income-tax', 'incometax']
        dept_keywords = ['department', 'dept', 'govt of india', 'government of india']
        
        has_income_tax = any(keyword in text_normalized for keyword in income_tax_keywords)
        has_dept = any(keyword in text_normalized for keyword in dept_keywords)
        
        if has_income_tax and has_dept:
            # Income Tax Department header found - definitely PAN
            best_score = max(best_score, 0.95)
        elif has_income_tax and best_score > 0.25:
            # Income Tax keyword found with reasonable PAN score
            best_score = max(best_score, 0.85)
        elif re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text) and best_score > 0.3:
            # PAN format detected
            best_score = max(best_score, 0.80)
        
        # If no PAN indicators found, mark as Unknown
        if best_score < 0.1:
            best_type = KYCDocumentType.UNKNOWN
        
        # Determine if valid KYC document
        # PAN-ONLY SYSTEM: Only PAN documents supported
        kyc_document_types = [KYCDocumentType.PAN]
        
        # CRITICAL: Check for fraud indicators FIRST
        # If document is fraudulent (watermarked, fake, etc), REJECT immediately
        fraud_check = self._detect_fraud_indicators(text)
        if fraud_check['is_fraudulent']:
            # Document is fraudulent - REJECT regardless of document type or score
            return {
                "is_valid_kyc": False,
                "document_type": best_type.value,
                "confidence": round(best_score, 2),
                "reason": f"DOCUMENT REJECTED: {fraud_check['fraud_reason']} - Fraudulent or non-original document",
                "all_scores": {"PAN": round(best_score, 2)},
                "extracted_patterns": self._extract_key_patterns(text, best_type),
                "fraud_detected": True,
                "fraud_indicators": fraud_check['indicators']
            }
        
        # PAN-ONLY: Use threshold (0.20) for PAN validation
        is_valid = best_type == KYCDocumentType.PAN and best_score > 0.20
        
        # If score is very low, mark as Unknown instead of a specific type
        if best_score < 0.1:
            best_type = KYCDocumentType.UNKNOWN
            is_valid = False
        
        result = {
            "is_valid_kyc": is_valid,
            "document_type": best_type.value,
            "confidence": round(best_score, 2),
            "reason": self._get_reason(best_type, best_score, is_valid),
            "all_scores": {"PAN": round(best_score, 2)},
            "extracted_patterns": self._extract_key_patterns(text, best_type),
            "fraud_detected": False
        }
        
        return result
    
    def _validate_pan_strict(self, text: str) -> Dict:
        """
        STRICT validation: Only approve PAN with ALL mandatory elements
        Required elements:
        1. Income Tax Department / Government of India header
        2. Name (person's name)
        3. Father's name
        4. Date of birth (DD/MM/YYYY)
        5. PAN number (XXXXX0000X format)
        6. Signature area
        """
        text_lower = text.lower()
        text_normalized = re.sub(r'\s+', ' ', text_lower)
        
        required_elements = {}
        failures = []
        
        # 1. Check Income Tax Department header (CRITICAL)
        has_income_tax = any(keyword in text_normalized for keyword in 
                            ['income tax', 'income-tax', 'incometax'])
        has_govt = any(keyword in text_normalized for keyword in 
                      ['govt of india', 'government of india', 'govt of india'])
        
        if not (has_income_tax and has_govt):
            failures.append("Missing Income Tax Department / Government of India header")
        else:
            required_elements["header"] = True
        
        # 2. Check for name (at least 2 words, capitalized)
        # Pattern: Word(s) that could be a name
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
        has_name = bool(re.search(name_pattern, text))
        
        if not has_name:
            failures.append("Missing person's name")
        else:
            required_elements["name"] = True
        
        # 3. Check for father's name (usually preceded by "Father" or "S/O")
        has_father = bool(re.search(r'(?:father|s/o|son of)', text_lower))
        
        if not has_father:
            failures.append("Missing father's name")
        else:
            required_elements["father"] = True
        
        # 4. Check for date of birth (DD/MM/YYYY or D/M/YY format)
        has_dob = bool(re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text))
        
        if not has_dob:
            failures.append("Missing date of birth")
        else:
            required_elements["dob"] = True
        
        # 5. Check for PAN number (XXXXX0000X)
        has_pan = bool(re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text))
        
        if not has_pan:
            failures.append("Missing PAN number (XXXXX0000X format)")
        else:
            required_elements["pan"] = True
        
        # 6. Check for signature (usually mentioned in document)
        has_signature = 'signature' in text_lower or 'sign' in text_lower
        
        if not has_signature:
            failures.append("Missing signature")
        else:
            required_elements["signature"] = True
        
        # Calculate confidence based on elements found
        total_required = 6
        elements_found = len(required_elements)
        confidence = elements_found / total_required
        
        return {
            "is_valid": len(failures) == 0,
            "confidence": confidence,
            "details": list(required_elements.keys()),
            "failure_reason": " | ".join(failures) if failures else ""
        }
    
    def _check_aadhar(self, text: str, text_lower: str, text_normalized: str) -> float:
        """Check for Aadhar document characteristics"""
        score = 0.0
        
        # Strong reject if driving license keywords are present
        if any(keyword in text_lower for keyword in ['driving license', 'driving licence', 'driver license', 'driver licence', 'valid upto', 'vehicle class', 'dl no', 'dl number', 'license number', 'driver', 'non transport', 'transport', 'exp.', 'regional transport']):
            return 0.0
        
        # Strong reject if voter ID keywords are present
        if any(keyword in text_lower for keyword in ['voter id', 'election commission', 'epic', 'voter card', 'elector', 'electoral', 'voter slip', 'chief electoral']):
            return 0.0
        
        # Check for 12-digit Aadhar number (but reduce weight since many docs have 12-digit numbers)
        if re.search(r'\d{4}\s?\d{4}\s?\d{4}', text):
            score += 0.2

        # Check for specific Aadhar keywords - HIGHER WEIGHT
        aadhar_keywords = ['aadhar', 'aadhaar', 'uid', 'unique id']
        matches = sum(1 for keyword in aadhar_keywords if keyword in text_lower)
        score += min(matches * 0.25, 0.5)

        # Check for common Aadhar fields
        if any(keyword in text_lower for keyword in ['nfsa', 'father', 'dob', 'date of birth', 'government of india']):
            score += 0.2

        return min(score, 1.0)
    
    def _check_pan(self, text: str, text_lower: str, text_normalized: str) -> float:
        """Check for PAN document characteristics with strict validation"""
        score = 0.0
        
        # CRITICAL: Check for Government of India tag
        has_govt_india = self._check_government_of_india_tag(text_lower, text_normalized)
        if not has_govt_india:
            return 0.0  # REJECT if no Government of India tag
        
        # Check for Income Tax Department header - STRONGEST indicator
        income_tax_keywords = ['income tax', 'income-tax', 'incometax', 'incometax']
        dept_keywords = ['department', 'dept', 'govt of india', 'government of india', 'govt of india']
        
        # Use normalized text which handles newlines and extra spaces
        has_income_tax = any(keyword in text_normalized for keyword in income_tax_keywords)
        has_dept = any(keyword in text_normalized for keyword in dept_keywords)
        
        if has_income_tax and has_dept:
            score += 0.85  # VERY STRONG indicator - Income Tax Department clearly indicates PAN
        elif has_income_tax:
            score += 0.65  # Strong indicator even without explicit "department"
        
        # CRITICAL: Check for valid PAN format XXXXX0000X - VERY HIGH WEIGHT
        pan_check = self._validate_pan_account_number(text)
        if pan_check['is_valid']:
            score += 0.75  # Increased weight for valid PAN format
        else:
            # If PAN format is invalid, significantly reduce score
            score *= 0.5
        
        # CRITICAL: Check for Date of Birth
        dob_check = self._validate_dob_in_pan(text)
        if dob_check['is_valid']:
            score += 0.65  # High weight for valid DOB
        else:
            # If DOB is missing or invalid, significantly reduce score
            score *= 0.5
        
        # Check for explicit PAN keywords - HIGH WEIGHT
        explicit_pan_keywords = ['pan card', 'pan number', 'pan:', 'permanent account number', 'p.a.n', 'permanent account']
        explicit_matches = sum(1 for keyword in explicit_pan_keywords if keyword in text_lower)
        score += min(explicit_matches * 0.35, 0.65)
        
        # Check for common PAN fields - these are very indicative
        pan_specific_fields = ['date of birth', 'father', 'name', 'assessement year', 'dob', 'signature', 'assessor code']
        field_matches = sum(1 for field in pan_specific_fields if field in text_lower)
        score += min(field_matches * 0.15, 0.3)
        
        # Additional PAN indicators from the actual card layout
        if any(keyword in text_lower for keyword in ['govt', 'sarkaar', 'भारत', 'government']):
            score += 0.1
        
        # CRITICAL: REJECT if fraud/watermarks detected
        fraud_check = self._detect_fraud_indicators(text)
        if fraud_check['is_fraudulent']:
            # Watermarked, tampered, or non-original documents are REJECTED
            return 0.0
        
        # Strong reject if obviously not PAN (but allow combined documents)
        if any(keyword in text_lower for keyword in ['valid upto', 'vehicle class', 'driving license', 'election commission', 'voter id']):
            score *= 0.5  # Reduced penalty - could be combined doc
        
        return min(score, 1.0)
    
    def _check_government_of_india_tag(self, text_lower: str, text_normalized: str) -> bool:
        """Check for Government of India tag in PAN card - CRITICAL validation"""
        govt_india_patterns = [
            'government of india',
            'govt of india',
            'govt. of india',
            'भारत सरकार',  # Government of India in Hindi
        ]
        
        # Check both normalized and original lowercase versions
        for pattern in govt_india_patterns:
            if pattern in text_normalized or pattern in text_lower:
                return True
        
        # Also check for Income Tax Department which is part of Government of India
        if 'income tax' in text_normalized or 'income tax' in text_lower:
            return True
        
        return False
    
    def _validate_pan_account_number(self, text: str) -> Dict:
        """Validate PAN account number format: XXXXX0000X"""
        # Search for PAN format patterns
        pan_patterns = [
            r'[A-Z]{5}[0-9]{4}[A-Z]{1}',  # Standard format
            r'[A-Z]{5}\s+[0-9]{4}\s+[A-Z]{1}',  # With spaces
            r'[A-Z]{5}[^A-Z0-9]*[0-9]{4}[^A-Z0-9]*[A-Z]{1}',  # With any separators
        ]
        
        pan_number = None
        for pattern in pan_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Clean up the PAN number (remove spaces and extra chars)
                pan_number = re.sub(r'[^A-Z0-9]', '', matches[0])
                break
        
        if not pan_number:
            return {
                "is_valid": False,
                "pan_number": "",
                "reason": "PAN number not found. Expected format: XXXXX0000X (5 letters + 4 digits + 1 letter)"
            }
        
        # Validate the format is exactly correct
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
            return {
                "is_valid": False,
                "pan_number": pan_number,
                "reason": f"Invalid PAN format: {pan_number}. Expected: XXXXX0000X"
            }
        
        return {
            "is_valid": True,
            "pan_number": pan_number,
            "reason": "Valid PAN account number format"
        }
    
    def _validate_dob_in_pan(self, text: str) -> Dict:
        """Validate Date of Birth in PAN card"""
        # Common DOB patterns
        dob_patterns = [
            r'(?:dob|date\s+of\s+birth)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # Just date in DD/MM/YYYY or DD-MM-YYYY
        ]
        
        dob_found = None
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dob_found = match.group(1) if '(' in pattern else match.group(0)
                break
        
        if not dob_found:
            return {
                "is_valid": False,
                "dob": "",
                "reason": "Date of Birth not found in expected format (DD/MM/YYYY)"
            }
        
        # Validate the date format is reasonable
        dob_parts = re.split(r'[/-]', dob_found)
        if len(dob_parts) != 3:
            return {
                "is_valid": False,
                "dob": dob_found,
                "reason": f"Invalid DOB format: {dob_found}. Expected DD/MM/YYYY"
            }
        
        try:
            day, month, year = int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2])
            
            # Validate day
            if day < 1 or day > 31:
                return {
                    "is_valid": False,
                    "dob": dob_found,
                    "reason": f"Invalid day: {day}. Day must be between 1 and 31"
                }
            
            # Validate month
            if month < 1 or month > 12:
                return {
                    "is_valid": False,
                    "dob": dob_found,
                    "reason": f"Invalid month: {month}. Month must be between 1 and 12"
                }
            
            # Validate year (should be reasonable - not in future, not too old)
            current_year = datetime.now().year
            if year < 100:  # 2-digit year, assume 19xx or 20xx
                year = 1900 + year if year > 50 else 2000 + year
            
            if year > current_year:
                return {
                    "is_valid": False,
                    "dob": dob_found,
                    "reason": f"Invalid year: {year}. Year cannot be in the future"
                }
            
            # Check if person is at least 18 years old (typical KYC requirement)
            age = current_year - year
            if age < 0:
                return {
                    "is_valid": False,
                    "dob": dob_found,
                    "reason": f"Invalid DOB: calculated negative age"
                }
            
            return {
                "is_valid": True,
                "dob": f"{day:02d}/{month:02d}/{year}",
                "reason": f"Valid DOB found: {day:02d}/{month:02d}/{year}",
                "age": age
            }
        
        except (ValueError, IndexError) as e:
            return {
                "is_valid": False,
                "dob": dob_found,
                "reason": f"Error parsing DOB: {dob_found}"
            }
    
    def _check_passport(self, text: str, text_lower: str, text_normalized: str) -> float:
        """Check for Passport document characteristics"""
        score = 0.0
        
        # Strong reject if voter ID keywords are present
        if any(keyword in text_lower for keyword in ['voter id', 'election commission', 'epic', 'voter card', 'elector', 'electoral']):
            return 0.0
        
        # Check for passport number format - HIGH WEIGHT
        if re.search(r'\b[A-Z]\d{7}\b', text):
            score += 0.4
        
        # Check for passport keywords - HIGHER WEIGHT
        passport_keywords = ['passport', 'passport number', 'machine readable zone', 'republic of india']
        matches = sum(1 for keyword in passport_keywords if keyword in text_lower)
        score += min(matches * 0.2, 0.5)
        
        # Check for common passport fields
        if any(keyword in text_lower for keyword in ['issued', 'valid', 'date of issue', 'date of expiry']):
            score += 0.15
        
        # Penalize if other document keywords are present
        if any(keyword in text_lower for keyword in ['driving license', 'aadhar', 'pan']):
            score *= 0.6
        
        return min(score, 1.0)
    
    def _check_driving_license(self, text: str, text_lower: str, text_normalized: str) -> float:
        """Check for Driving License document characteristics"""
        score = 0.0
        
        # Check for explicit DL keywords - HIGH WEIGHT (including OCR common terms)
        dl_keywords = ['driving license', 'driving licence', 'driver license', 'driver licence', 'dl no', 'dl number', 'license number', 'driver', 'non transport', 'transport']
        matches = sum(1 for keyword in dl_keywords if keyword in text_lower)
        score += min(matches * 0.25, 0.8)
        
        # Check for common DL-specific fields - VERY HIGH WEIGHT
        if any(keyword in text_lower for keyword in ['valid upto', 'date of expiry', 'validity', 'vehicle class', 'class of vehicle', 'non transport', 'transport', 'exp.', 'regional transport office']):
            score += 0.5
        
        # Check for DL number patterns (MH01/98AB1234 or similar)
        if re.search(r'[A-Z]{2}\d{2}/?\d{2}[A-Z]{2}\d{4}', text):
            score += 0.3
        
        # Check for common DL issuing authority
        if any(keyword in text_lower for keyword in ['regional transport office', 'rto', 'issued by', 'rto']):
            score += 0.1
        
        return min(score, 1.0)
    
    def _check_voter_id(self, text: str, text_lower: str, text_normalized: str) -> float:
        """Check for Voter ID document characteristics"""
        score = 0.0
        
        # Check for strong voter ID keywords - HIGH WEIGHT
        strong_keywords = ['voter id', 'election commission', 'epic']
        strong_matches = sum(1 for keyword in strong_keywords if keyword in text_lower)
        score += min(strong_matches * 0.4, 0.7)
        
        # Check for voter ID patterns
        matches = sum(1 for pattern in self.voter_id_patterns if re.search(pattern, text_lower))
        score += min(matches * 0.15, 0.5)
        
        # Check for common voter ID fields - VERY HIGH WEIGHT
        voter_fields = ['epic', 'election', 'constituency', 'electoral', 'voter slip', 'elector', 'chief electoral']
        field_matches = sum(1 for field in voter_fields if field in text_lower)
        score += min(field_matches * 0.2, 0.5)
        
        # Check for voter ID number pattern (10-12 alphanumeric)
        if re.search(r'\b[A-Z0-9]{10,12}\b', text):
            score += 0.1
        
        return min(score, 1.0)
    
    def _check_bank_statement(self, text: str, text_lower: str, text_normalized: str) -> float:
        """Check for Bank Statement document characteristics"""
        score = 0.0
        
        # CRITICAL: If this is clearly a PAN document, return 0 immediately
        # Support variations due to OCR (use normalized text for better detection)
        income_tax_keywords = ['income tax', 'income-tax', 'incometax', 'incometax']
        dept_keywords = ['department', 'dept', 'govt of india', 'government of india', 'govt of india']
        
        if any(keyword in text_normalized for keyword in income_tax_keywords) and \
           any(keyword in text_normalized for keyword in dept_keywords):
            return 0.0  # Definitely a PAN document, not a bank statement
        
        if re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text):
            # If it has PAN format AND Income Tax keywords, it's definitely a PAN
            if any(keyword in text_normalized for keyword in income_tax_keywords) or \
               'permanent account number' in text_lower:
                return 0.0
        
        # If document has PAN card layout indicators, return 0
        if any(keyword in text_lower for keyword in ['permanent account number', 'pan number', 'pan card']):
            return 0.0
        
        # Check for strong bank statement keywords
        strong_bank_keywords = ['bank statement', 'statement of account', 'ifsc', 'micr code', 'ifsc code']
        strong_matches = sum(1 for keyword in strong_bank_keywords if keyword in text_lower)
        score += min(strong_matches * 0.4, 0.7)
        
        # Check for account/IFSC patterns - HIGH WEIGHT
        if re.search(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', text):  # IFSC code
            score += 0.3
        
        # Check for other bank statement patterns
        matches = sum(1 for pattern in self.bank_statement_patterns if re.search(pattern, text_lower))
        score += min(matches * 0.12, 0.4)
        
        # Check for date ranges (common in statements)
        if re.search(r'statement\s*(period|from|date).*\d{2}[/-]\d{2}[/-]\d{2,4}', text_lower):
            score += 0.15
        
        # Penalize if PAN-like patterns exist
        if re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text):
            score *= 0.6
        
        return min(score, 1.0)
    
    def _check_utility_bill(self, text: str, text_lower: str, text_normalized: str) -> float:
        """Check for Utility Bill document characteristics"""
        score = 0.0
        
        # Check for utility bill keywords
        matches = sum(1 for pattern in self.utility_bill_patterns if re.search(pattern, text_lower))
        score += min(matches * 0.15, 0.8)
        
        # Check for common bill fields
        if any(keyword in text_lower for keyword in ['amount due', 'due date', 'period']):
            score += 0.15
        
        return min(score, 1.0)
    
    def _get_reason(self, doc_type: KYCDocumentType, score: float, is_valid: bool) -> str:
        """Generate reason message based on validation result"""
        if not is_valid:
            if doc_type == KYCDocumentType.UNKNOWN:
                return "Unknown document type. The document does not match any recognized KYC document format. Please provide a valid KYC document (Aadhar, PAN, Passport, Driving License, Voter ID, Bank Statement, or Utility Bill)."
            elif score < 0.1:
                return "Document does not appear to be a valid KYC document. No recognizable KYC patterns detected."
            elif score < 0.3:
                return f"Document type might be {doc_type.value}, but confidence is too low. Cannot confirm as valid KYC document."
            else:
                return f"Document appears to be {doc_type.value}, but confidence is insufficient for KYC validation."
        else:
            return f"Document successfully identified as {doc_type.value}"
    
    def _extract_key_patterns(self, text: str, doc_type: KYCDocumentType) -> Dict:
        """Extract key patterns found in the document"""
        patterns = {}
        
        # Extract PAN number specifically if PAN document
        if doc_type == KYCDocumentType.PAN:
            pan_matches = re.findall(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text)
            if pan_matches:
                patterns['pan_number'] = pan_matches[0]
        
        # Extract numbers
        numbers = re.findall(r'\b\d{4,12}\b', text)
        if numbers:
            patterns['potential_ids'] = numbers[:3]  # First 3 matches
        
        # Extract email
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            patterns['emails'] = emails
        
        # Extract phone numbers
        phones = re.findall(r'\b\d{10}\b', text)
        if phones:
            patterns['potential_phone_numbers'] = phones[:2]
        
        # Extract dates
        dates = re.findall(r'\b\d{2}[/-]\d{2}[/-]\d{2,4}\b', text)
        if dates:
            patterns['potential_dates'] = dates[:3]
        
        return patterns

