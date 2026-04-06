"""
Mock PAN Validation API
Provides pre-defined validation responses for testing without external API calls
Used by Verify Agent for development and testing
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import re
from enum import Enum

class ValidationStatus(Enum):
    """Validation status enumeration"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"
    WARNING = "WARNING"


class MockValidationResponse:
    """Represents a mock validation response"""
    
    def __init__(self, pan_number: str, name: str, status: str, confidence: float, details: Dict[str, Any]):
        self.pan_number = pan_number
        self.name = name
        self.status = status
        self.confidence = confidence
        self.details = details
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary response"""
        return {
            "pan_number": self.pan_number,
            "name": self.name,
            "status": self.status,
            "confidence": self.confidence,
            "details": self.details,
            "timestamp": self.timestamp,
            "is_mock": True,
            "mock_api_version": "1.0"
        }


class MockPANValidator:
    """Mock PAN Validator with pre-defined test cases"""
    
    def __init__(self):
        """Initialize mock validator with test data"""
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self) -> Dict[str, Dict[str, Any]]:
        """Load pre-defined test cases for PAN validation"""
        return {
            # Valid PAN - From the sample data provided
            "CYMPB5839A": {
                "name": "BORUGULA SURESH",
                "father_name": "BORUGULA MUNASWAMY",
                "dob": "06/03/1992",
                "status": ValidationStatus.APPROVED.value,
                "confidence": 0.98,
                "reason": "Valid PAN - All required fields present and verified",
                "checks_passed": [
                    "PAN format valid (5 letters + 4 digits + 1 letter)",
                    "Government of India verification tag present",
                    "Name field present and readable",
                    "Father's name present",
                    "Date of Birth valid (06/03/1992)",
                    "Photo present",
                    "Signature present",
                    "No fraud indicators detected"
                ],
                "checks_failed": [],
                "fraud_score": 0.0,
                "is_original": True
            },
            
            # Valid PAN - Generic test case
            "ABCDE1234F": {
                "name": "JOHN DOE",
                "father_name": "JAMES DOE",
                "dob": "15/08/1985",
                "status": ValidationStatus.APPROVED.value,
                "confidence": 0.95,
                "reason": "Valid PAN - Document verification successful",
                "checks_passed": [
                    "PAN format valid",
                    "Government of India verification passed",
                    "Name verified",
                    "Father's name verified",
                    "Date of Birth valid (Age: 38 years)",
                    "Photo present and clear",
                    "Signature verified",
                    "No tampering detected"
                ],
                "checks_failed": [],
                "fraud_score": 0.0,
                "is_original": True
            },
            
            # Invalid PAN - Wrong format
            "INVALID123": {
                "name": None,
                "father_name": None,
                "dob": None,
                "status": ValidationStatus.REJECTED.value,
                "confidence": 0.05,
                "reason": "REJECTED - Invalid PAN format. Expected format: XXXXX0000X",
                "checks_passed": [],
                "checks_failed": [
                    "PAN format invalid - does not match XXXXX0000X pattern",
                    "Name field not found or unreadable",
                    "Father's name not found",
                    "Date of Birth not found"
                ],
                "fraud_score": 0.8,
                "is_original": False
            },
            
            # Watermarked/Sample PAN
            "SAMPLE123X": {
                "name": "SAMPLE USER",
                "father_name": "SAMPLE FATHER",
                "dob": "01/01/2000",
                "status": ValidationStatus.REJECTED.value,
                "confidence": 0.02,
                "reason": "REJECTED - Document is a SAMPLE/WATERMARKED document. Not valid for KYC.",
                "checks_passed": [],
                "checks_failed": [
                    "Document marked as SAMPLE - for demonstration only",
                    "Watermark detected - not original",
                    "Not suitable for actual KYC verification"
                ],
                "fraud_score": 0.95,
                "is_original": False,
                "is_sample": True
            },
            
            # Photocopy PAN
            "PHOTOCOPY01": {
                "name": "PHOTOCOPY USER",
                "father_name": "PHOTOCOPY FATHER",
                "dob": "05/07/1995",
                "status": ValidationStatus.REJECTED.value,
                "confidence": 0.1,
                "reason": "REJECTED - Document is a photocopy/non-original. Only original documents accepted.",
                "checks_passed": ["PAN format appears valid"],
                "checks_failed": [
                    "Document detected as photocopy - not original",
                    "Photocopy quality degradation detected",
                    "Original document required for KYC"
                ],
                "fraud_score": 0.85,
                "is_original": False,
                "is_photocopy": True
            },
            
            # Expired/Cancelled PAN
            "EXPIRY123A": {
                "name": "EXPIRED USER",
                "father_name": "EXPIRED FATHER",
                "dob": "12/10/1980",
                "status": ValidationStatus.REJECTED.value,
                "confidence": 0.15,
                "reason": "REJECTED - PAN document appears expired or cancelled.",
                "checks_passed": ["PAN format valid"],
                "checks_failed": [
                    "Document marked as expired",
                    "Validity period exceeded",
                    "Not valid for current KYC verification"
                ],
                "fraud_score": 0.4,
                "is_original": True,
                "is_expired": True
            },
            
            # Missing signature
            "NOSIGN123C": {
                "name": "NO SIGNATURE USER",
                "father_name": "NO SIGNATURE FAT",
                "dob": "20/05/1990",
                "status": ValidationStatus.REJECTED.value,
                "confidence": 0.25,
                "reason": "REJECTED - Signature missing. All required fields must be present.",
                "checks_passed": [
                    "PAN format valid",
                    "Name present",
                    "Father's name present",
                    "Date of Birth valid"
                ],
                "checks_failed": [
                    "Signature field missing or illegible",
                    "Critical document element missing"
                ],
                "fraud_score": 0.6,
                "is_original": True
            },
            
            # Missing photo
            "NOPHOTO12D": {
                "name": "NO PHOTO USER",
                "father_name": "NO PHOTO FATHER",
                "dob": "15/12/1988",
                "status": ValidationStatus.REJECTED.value,
                "confidence": 0.2,
                "reason": "REJECTED - Photo missing. Photo is essential for identity verification.",
                "checks_passed": [
                    "PAN format valid",
                    "Name present",
                    "Father's name present"
                ],
                "checks_failed": [
                    "Photo field missing or not visible",
                    "Identity verification impossible without photo"
                ],
                "fraud_score": 0.7,
                "is_original": True
            },
            
            # Warning case - Low quality but acceptable
            "LOWQUAL22E": {
                "name": "LOW QUALITY USER",
                "father_name": "LOW QUALITY FAT",
                "dob": "08/09/1993",
                "status": ValidationStatus.WARNING.value,
                "confidence": 0.65,
                "reason": "WARNING - Document quality is low but readable. Proceed with caution.",
                "checks_passed": [
                    "PAN format valid",
                    "Basic information readable",
                    "No fraud indicators"
                ],
                "checks_failed": [],
                "warnings": [
                    "Image quality is degraded",
                    "Some text partially unclear",
                    "Manual verification recommended"
                ],
                "fraud_score": 0.15,
                "is_original": True
            },
            
            # Data Mismatch Test Case - Different person's data
            "BWZPS1234R": {
                "name": "TWITTERPREET SINGH",
                "father_name": "BALWINDER SINGH",
                "dob": "14/05/1995",
                "status": ValidationStatus.REJECTED.value,
                "confidence": 0.0,
                "reason": "REJECTED - PAN number found but not in approved database. Data mismatch with approved records.",
                "checks_passed": [
                    "PAN format valid (BWZPS1234R)"
                ],
                "checks_failed": [
                    "PAN number not approved",
                    "Data does not match approved test records",
                    f"Provided: Name=TWITTERPREET SINGH, DOB=14/05/1995",
                    "Only pre-defined test PANs return APPROVED in mock mode"
                ],
                "fraud_score": 0.5,
                "is_original": False
            }
        }
    
    def validate_pan(self, pan_number: str, name: Optional[str] = None, 
                     dob: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate PAN with mock pre-defined responses
        
        Args:
            pan_number: PAN number to validate
            name: Optional person name for verification
            dob: Optional date of birth for verification
            
        Returns:
            Validation response dictionary
        """
        pan_upper = pan_number.strip().upper() if pan_number else ""
        
        # Check if we have a test case for this PAN
        if pan_upper in self.test_cases:
            test_case = self.test_cases[pan_upper]
            response = MockValidationResponse(
                pan_number=pan_upper,
                name=test_case.get("name"),
                status=test_case.get("status"),
                confidence=test_case.get("confidence"),
                details={
                    "father_name": test_case.get("father_name"),
                    "dob": test_case.get("dob"),
                    "reason": test_case.get("reason"),
                    "checks_passed": test_case.get("checks_passed", []),
                    "checks_failed": test_case.get("checks_failed", []),
                    "warnings": test_case.get("warnings", []),
                    "fraud_score": test_case.get("fraud_score", 0.0),
                    "is_original": test_case.get("is_original", False),
                    "is_sample": test_case.get("is_sample", False),
                    "is_photocopy": test_case.get("is_photocopy", False),
                    "is_expired": test_case.get("is_expired", False)
                }
            )
            return response.to_dict()
        
        # For unknown PANs, generate a response based on format
        return self._validate_unknown_pan(pan_upper, name, dob)
    
    def _validate_unknown_pan(self, pan_number: str, name: Optional[str] = None, 
                             dob: Optional[str] = None) -> Dict[str, Any]:
        """Generate validation response for unknown PAN numbers"""
        
        # Check PAN format
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        if not re.match(pan_pattern, pan_number):
            response = MockValidationResponse(
                pan_number=pan_number,
                name=None,
                status=ValidationStatus.REJECTED.value,
                confidence=0.0,
                details={
                    "reason": f"REJECTED - Invalid PAN format. Expected format: XXXXX0000X, got: {pan_number}",
                    "checks_passed": [],
                    "checks_failed": [
                        "PAN format does not match XXXXX0000X pattern",
                        "Cannot validate further with invalid format"
                    ],
                    "fraud_score": 0.9,
                    "is_original": False
                }
            )
            return response.to_dict()
        
        # STRICT MODE: PAN not in test cases = REJECTED (even with valid format)
        # This ensures only pre-defined test PANs are approved
        response = MockValidationResponse(
            pan_number=pan_number,
            name=name or None,
            status=ValidationStatus.REJECTED.value,
            confidence=0.0,
            details={
                "reason": f"REJECTED - PAN '{pan_number}' not found in approved database. Only pre-defined PANs are approved.",
                "checks_passed": [
                    "PAN format is valid (5 letters + 4 digits + 1 letter)"
                ],
                "checks_failed": [
                    "PAN number not in approved database",
                    "This mock API only approves pre-defined test PANs",
                    f"Provided data: Name={name}, DOB={dob}"
                ],
                "warnings": [
                    "MOCK MODE: Only pre-defined PANs return APPROVED status",
                    "Use one of the test PANs for approval",
                    "Real API would perform actual validation"
                ],
                "fraud_score": 0.5,
                "is_original": False,
                "available_test_pans": list(self.test_cases.keys())
            }
        )
        return response.to_dict()
    
    def get_test_cases(self) -> Dict[str, str]:
        """Get list of available test cases"""
        return {
            pan: test_case.get("status")
            for pan, test_case in self.test_cases.items()
        }
    
    def batch_validate_pans(self, pan_list: list) -> Dict[str, Any]:
        """
        Validate multiple PANs
        
        Args:
            pan_list: List of PAN numbers to validate
            
        Returns:
            Dictionary with validation results for each PAN
        """
        results = {
            "total": len(pan_list),
            "validated_at": datetime.now().isoformat(),
            "validations": []
        }
        
        for pan in pan_list:
            result = self.validate_pan(pan)
            results["validations"].append(result)
        
        # Summary statistics
        approved = sum(1 for v in results["validations"] if v["status"] == ValidationStatus.APPROVED.value)
        rejected = sum(1 for v in results["validations"] if v["status"] == ValidationStatus.REJECTED.value)
        pending = sum(1 for v in results["validations"] if v["status"] == ValidationStatus.PENDING.value)
        
        results["summary"] = {
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "approval_rate": f"{(approved/len(pan_list)*100):.1f}%" if pan_list else "0%"
        }
        
        return results


# Initialize global validator instance
mock_validator = MockPANValidator()


def validate_pan_mock(pan_number: str, name: Optional[str] = None, 
                     dob: Optional[str] = None) -> Dict[str, Any]:
    """
    Standalone function to validate PAN using mock API
    
    Usage:
        response = validate_pan_mock("CYMPB5839A", name="BORUGULA SURESH")
    """
    return mock_validator.validate_pan(pan_number, name, dob)


def get_mock_test_cases() -> Dict[str, str]:
    """Get list of all available test cases"""
    return mock_validator.get_test_cases()


# Example usage and documentation
if __name__ == "__main__":
    print("=" * 70)
    print("MOCK PAN VALIDATION API - Test Cases")
    print("=" * 70)
    
    validator = MockPANValidator()
    test_cases = validator.get_test_cases()
    
    print("\nAvailable Test Cases:")
    for pan, status in test_cases.items():
        print(f"  {pan:<15} → {status}")
    
    print("\n" + "=" * 70)
    print("Example Validations:")
    print("=" * 70)
    
    # Test with valid PAN from sample data
    print("\n1. Valid PAN (From Sample Data):")
    result = validator.validate_pan("CYMPB5839A")
    print(json.dumps(result, indent=2))
    
    # Test with sample/watermarked PAN
    print("\n2. Watermarked/Sample PAN:")
    result = validator.validate_pan("SAMPLE123X")
    print(json.dumps(result, indent=2))
    
    # Test with invalid format
    print("\n3. Invalid Format PAN:")
    result = validator.validate_pan("INVALID123")
    print(json.dumps(result, indent=2))
    
    # Test batch validation
    print("\n4. Batch Validation:")
    pan_list = ["CYMPB5839A", "SAMPLE123X", "ABCDE1234F", "INVALID123"]
    result = validator.batch_validate_pans(pan_list)
    print(json.dumps(result, indent=2))
