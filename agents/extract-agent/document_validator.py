"""
Document Type Recognition and Validation Module
Identifies KYC document types and validates if documents are valid KYC documents
"""

import re
from typing import Dict
from enum import Enum

class KYCDocumentType(Enum):
    """Supported KYC document types in India"""
    AADHAR = "Aadhar"
    PAN = "PAN"
    PASSPORT = "Passport"
    DRIVING_LICENSE = "Driving License"
    VOTER_ID = "Voter ID"
    BANK_STATEMENT = "Bank Statement"
    UTILITY_BILL = "Utility Bill"
    UNKNOWN = "Unknown"
    INVALID = "Invalid"

class DocumentValidator:
    """Validates and classifies KYC documents"""
    
    def __init__(self):
        """Initialize document patterns for recognition"""
        self.aadhar_patterns = [
            r'\b\d{4}\s?\d{4}\s?\d{4}\b',  # 12 digit Aadhar
            r'aadhar',
            r'aadhaar',
            r'uid',
            r'unique\s*id',
        ]
        
        self.pan_patterns = [
            r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',  # PAN format
            r'pan\s*card',
            r'pan\s*number',
            r'permanent\s*account\s*number',
        ]
        
        self.passport_patterns = [
            r'\bA\d{8}\b',  # Indian passport format
            r'passport',
            r'passport\s*number',
            r'machine\s*readable\s*zone',
        ]
        
        self.driving_license_patterns = [
            r'driving\s*license',
            r'driving\s*licence',
            r'dl\s*number',
            r'license\s*number',
            r'valid\s*upto',
        ]
        
        self.voter_id_patterns = [
            r'voter\s*id',
            r'election\s*commission',
            r'epic\s*number',
            r'voter\s*card',
            r'epic',
            r'elector',
            r'electoral',
            r'voter\s*slip',
            r'voter\s*list',
            r'chief\s*electoral',
        ]
        
        self.bank_statement_patterns = [
            r'bank\s*statement',
            r'account\s*number',
            r'ifsc',
            r'micr',
            r'statement\s*period',
            r'balance',
        ]
        
        self.utility_bill_patterns = [
            r'utility\s*bill',
            r'electricity\s*bill',
            r'water\s*bill',
            r'telephone\s*bill',
            r'consumer\s*number',
            r'bill\s*amount',
        ]

    def _detect_fraud_indicators(self, text: str) -> Dict:
        """
        Detect fraud indicators in document
        Returns dict with fraud status and indicators found
        """
        text_lower = text.lower()
        fraud_indicators = []
        is_fraudulent = False
        
        # CRITICAL: Watermark/Sample document indicators
        watermark_keywords = [
            ('sample', 'Sample/Demo document watermark'),
            ('immihelp', 'Document sharing website watermark'),
            ('example', 'Example document watermark'),
            ('template', 'Template document'),
            ('draft', 'Draft document'),
            ('test', 'Test document'),
            ('dummy', 'Dummy/Fake document'),
            ('fake', 'Fake document'),
            ('not real', 'Not real indicator'),
            ('for demonstration', 'Demonstration document'),
            ('for reference only', 'Reference only'),
        ]
        
        for keyword, description in watermark_keywords:
            if keyword in text_lower:
                fraud_indicators.append(description)
                is_fraudulent = True
        
        # Second-level fraud indicators (inconsistencies, suspicious patterns)
        suspicious_patterns = [
            (r'copy\s+of\s+original', 'Copy of original (not certified)'),
            (r'photocopy', 'Photocopy (not original)'),
            (r'scanned\s+copy', 'Scanned copy'),
            (r'not\s+for\s+legal\s+purpose', 'Not for legal purpose'),
        ]
        
        for pattern, description in suspicious_patterns:
            if re.search(pattern, text_lower):
                fraud_indicators.append(description)
        
        # Determine fraud reason
        fraud_reason = "sample/fake document" if is_fraudulent else ""
        if fraud_indicators:
            fraud_reason = " + ".join(fraud_indicators[:2])  # Show top 2 indicators
        
        return {
            "is_fraudulent": is_fraudulent,
            "fraud_reason": fraud_reason,
            "indicators": fraud_indicators
        }

    def validate_and_classify(self, text: str) -> Dict:
        """
        Validate if document is a KYC document and classify its type
        
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
        
        # CRITICAL: Check for FRAUD INDICATORS first
        fraud_check = self._detect_fraud_indicators(text)
        if fraud_check["is_fraudulent"]:
            return {
                "is_valid_kyc": False,
                "document_type": KYCDocumentType.INVALID.value,
                "confidence": 0.0,
                "reason": f"🛑 FRAUD DETECTED: {fraud_check['fraud_reason']}",
                "fraud_indicators": fraud_check["indicators"],
                "details": []
            }
        
        # Normalize text for matching - convert newlines and extra spaces to single spaces
        text_lower = text.lower()
        # First, normalize whitespace (including newlines, tabs, etc.) to single spaces
        text_normalized = re.sub(r'\s+', ' ', text_lower)  # Replace multiple whitespace chars with single space
        text_normalized = re.sub(r'[^a-z0-9\s]', ' ', text_normalized)  # Remove special characters
        text_normalized = re.sub(r'\s+', ' ', text_normalized)  # Clean up again after removing special chars
        
        # Check each document type
        scores = {}
        details = {}
        
        scores[KYCDocumentType.AADHAR] = self._check_aadhar(text, text_lower, text_normalized)
        scores[KYCDocumentType.PAN] = self._check_pan(text, text_lower, text_normalized)
        scores[KYCDocumentType.PASSPORT] = self._check_passport(text, text_lower, text_normalized)
        scores[KYCDocumentType.DRIVING_LICENSE] = self._check_driving_license(text, text_lower, text_normalized)
        scores[KYCDocumentType.VOTER_ID] = self._check_voter_id(text, text_lower, text_normalized)
        scores[KYCDocumentType.BANK_STATEMENT] = self._check_bank_statement(text, text_lower, text_normalized)
        scores[KYCDocumentType.UTILITY_BILL] = self._check_utility_bill(text, text_lower, text_normalized)
        
        # Find best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Special logic: If Income Tax Department is found, ALWAYS prioritize PAN
        # Support OCR variations (use normalized text for better detection)
        income_tax_keywords = ['income tax', 'income-tax', 'incometax', 'incometax']
        dept_keywords = ['department', 'dept', 'govt of india', 'government of india', 'govt of india']
        
        has_income_tax = any(keyword in text_normalized for keyword in income_tax_keywords)
        has_dept = any(keyword in text_normalized for keyword in dept_keywords)
        
        if has_income_tax and has_dept:
            # Income Tax Department header is present - definitely a PAN
            best_type = KYCDocumentType.PAN
            best_score = max(scores[KYCDocumentType.PAN], 0.95)  # Very high confidence
        elif has_income_tax and scores[KYCDocumentType.PAN] > 0.25:
            # Income Tax keyword present with reasonable PAN score
            best_type = KYCDocumentType.PAN
            best_score = max(scores[KYCDocumentType.PAN], 0.85)
        elif re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text) and scores[KYCDocumentType.PAN] > 0.3:
            # PAN format detected with reasonable score
            best_type = KYCDocumentType.PAN
            best_score = max(scores[KYCDocumentType.PAN], 0.80)
        
        # Determine if valid KYC document
        kyc_document_types = [
            KYCDocumentType.AADHAR,
            KYCDocumentType.PAN,
            KYCDocumentType.PASSPORT,
            KYCDocumentType.DRIVING_LICENSE,
            KYCDocumentType.VOTER_ID,
            KYCDocumentType.BANK_STATEMENT,
            KYCDocumentType.UTILITY_BILL,
        ]
        
        # Special handling for PAN documents - they're primary KYC documents
        # Use lower threshold (0.20) for PAN since it's a critical document
        if best_type == KYCDocumentType.PAN:
            is_valid = best_score > 0.20
        else:
            is_valid = best_type in kyc_document_types and best_score > 0.3
        
        # If score is very low, mark as Unknown instead of a specific type
        if best_score < 0.1:
            best_type = KYCDocumentType.UNKNOWN
        
        result = {
            "is_valid_kyc": is_valid,
            "document_type": best_type.value,
            "confidence": round(best_score, 2),
            "reason": self._get_reason(best_type, best_score, is_valid),
            "all_scores": {doc_type.value: round(score, 2) for doc_type, score in scores.items()},
            "extracted_patterns": self._extract_key_patterns(text, best_type)
        }
        
        return result
    
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
        """Check for PAN document characteristics"""
        score = 0.0
        
        # CRITICAL: Check for Income Tax Department header - STRONGEST indicator
        # Support variations due to OCR (use text_normalized to handle newlines and extra spaces)
        income_tax_keywords = ['income tax', 'income-tax', 'incometax', 'incometax']
        dept_keywords = ['department', 'dept', 'govt of india', 'government of india', 'govt of india']
        
        # Use normalized text which handles newlines and extra spaces
        has_income_tax = any(keyword in text_normalized for keyword in income_tax_keywords)
        has_dept = any(keyword in text_normalized for keyword in dept_keywords)
        
        if has_income_tax and has_dept:
            score += 0.85  # VERY STRONG indicator - Income Tax Department clearly indicates PAN
        elif has_income_tax:
            score += 0.65  # Strong indicator even without explicit "department"
        
        # Check for PAN format XXXXX0000X - VERY HIGH WEIGHT
        # Also support formats with spaces or special chars that OCR might introduce
        pan_formats = [
            re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text),  # Standard format
            re.search(r'[A-Z]{5}\s*[0-9]{4}\s*[A-Z]{1}', text),  # With spaces
            re.search(r'[A-Z]{5}[^A-Z0-9]*[0-9]{4}[^A-Z0-9]*[A-Z]{1}', text),  # With any separators
        ]
        
        if any(pan_formats):
            score += 0.75  # Increased weight for PAN format
        
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
        
        # Strong reject if obviously not PAN (but allow combined documents)
        if any(keyword in text_lower for keyword in ['valid upto', 'vehicle class', 'driving license', 'election commission', 'voter id']):
            score *= 0.5  # Reduced penalty - could be combined doc
        
        return min(score, 1.0)
    
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

