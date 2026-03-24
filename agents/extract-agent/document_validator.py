"""
Document Type Recognition and Validation Module
Identifies KYC document types and validates if documents are valid KYC documents
"""

import re
from typing import Dict, List, Tuple
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
        
        # Normalize text for matching
        text_lower = text.lower()
        text_normalized = re.sub(r'[^a-z0-9\s]', ' ', text_lower)
        
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
        # Use lower threshold (0.25) for PAN since it's a critical document
        if best_type == KYCDocumentType.PAN:
            is_valid = best_score > 0.25
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
        
        # Check for PAN format XXXXX0000X - VERY HIGH WEIGHT
        # Also support formats with spaces or special chars that OCR might introduce
        pan_formats = [
            re.search(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', text),  # Standard format
            re.search(r'[A-Z]{5}\s*[0-9]{4}\s*[A-Z]{1}', text),  # With spaces
            re.search(r'[A-Z]{5}[^A-Z0-9]*[0-9]{4}[^A-Z0-9]*[A-Z]{1}', text),  # With any separators
        ]
        
        if any(pan_formats):
            score += 0.6  # Increased weight for PAN format
        
        # Check for PAN keywords - HIGH WEIGHT
        pan_keywords = ['pan card', 'pan number', 'permanent account number', 'income tax', 'pan', 'income tax department']
        matches = sum(1 for keyword in pan_keywords if keyword in text_lower)
        score += min(matches * 0.25, 0.5)
        
        # Check for common PAN fields
        if any(keyword in text_lower for keyword in ['date of birth', 'father', 'name', 'assessement year', 'dob']):
            score += 0.15
        
        # Check for presence of actual income tax document indicators
        if any(keyword in text_lower for keyword in ['income tax', 'income tax department', 'government of india']):
            score += 0.2
        
        # Slight penalize if other document keywords are present (but don't kill the score)
        if any(keyword in text_lower for keyword in ['driving license', 'aadhar', 'passport', 'voter id']):
            score *= 0.8  # Reduced penalty
        
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
        
        # Check for bank statement keywords
        matches = sum(1 for pattern in self.bank_statement_patterns if re.search(pattern, text_lower))
        score += min(matches * 0.15, 0.8)
        
        # Check for account/IFSC patterns
        if re.search(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', text):  # IFSC code
            score += 0.2
        
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

