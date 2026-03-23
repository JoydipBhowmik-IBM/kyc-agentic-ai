"""
Test script for document validator improvements
Tests the classification accuracy for different document types
"""

import sys
sys.path.append('agents/extract-agent')

from document_validator import DocumentValidator

def test_driving_license():
    """Test Driving License classification"""
    validator = DocumentValidator()
    
    # Sample Driving License text
    driving_license_text = """
    DRIVING LICENSE
    License No: MH01/98AB1234
    Name: JOHN DOE
    Address: 123 Main Street, Mumbai
    Date of Birth: 15/05/1990
    Valid Upto: 14/05/2030
    Class of Vehicle: Private
    Non Transport
    Date of Issue: 15/05/2015
    Issued By: Regional Transport Office
    """
    
    result = validator.validate_and_classify(driving_license_text)
    
    print("=" * 60)
    print("TEST 1: Driving License Classification")
    print("=" * 60)
    print(f"Document Type: {result['document_type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Is Valid KYC: {result['is_valid_kyc']}")
    print(f"Reason: {result['reason']}")
    print(f"\nAll Scores:")
    for doc_type, score in result['all_scores'].items():
        print(f"  {doc_type}: {score}")
    
    # Assertions
    assert result['document_type'] == 'Driving License', f"Expected Driving License, got {result['document_type']}"
    assert result['confidence'] >= 0.6, f"Expected confidence >= 0.6, got {result['confidence']}"
    assert result['is_valid_kyc'] == True, "Should be valid KYC"
    
    print("\n✅ TEST PASSED: Driving License correctly identified")
    return True


def test_aadhar():
    """Test Aadhar classification"""
    validator = DocumentValidator()
    
    # Sample Aadhar text
    aadhar_text = """
    AADHAR CARD
    Unique ID: 1234 5678 9012
    Name: JANE SMITH
    Father: SMITH SENIOR
    Date of Birth: 20/03/1985
    Gender: Female
    UID: 123456789012
    Government of India
    NFSA: Yes
    """
    
    result = validator.validate_and_classify(aadhar_text)
    
    print("\n" + "=" * 60)
    print("TEST 2: Aadhar Classification")
    print("=" * 60)
    print(f"Document Type: {result['document_type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Is Valid KYC: {result['is_valid_kyc']}")
    print(f"Reason: {result['reason']}")
    print(f"\nAll Scores:")
    for doc_type, score in result['all_scores'].items():
        print(f"  {doc_type}: {score}")
    
    # Assertions
    assert result['document_type'] == 'Aadhar', f"Expected Aadhar, got {result['document_type']}"
    assert result['confidence'] >= 0.5, f"Expected confidence >= 0.5, got {result['confidence']}"
    assert result['is_valid_kyc'] == True, "Should be valid KYC"
    
    print("\n✅ TEST PASSED: Aadhar correctly identified")
    return True


def test_pan_card():
    """Test PAN Card classification"""
    validator = DocumentValidator()
    
    # Sample PAN text
    pan_text = """
    PAN CARD
    PAN Number: ABCDE1234F
    Name: PERSON NAME
    Date of Birth: 01/01/1990
    Father Name: FATHER NAME
    Income Tax Department
    """
    
    result = validator.validate_and_classify(pan_text)
    
    print("\n" + "=" * 60)
    print("TEST 3: PAN Card Classification")
    print("=" * 60)
    print(f"Document Type: {result['document_type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Is Valid KYC: {result['is_valid_kyc']}")
    print(f"Reason: {result['reason']}")
    print(f"\nAll Scores:")
    for doc_type, score in result['all_scores'].items():
        print(f"  {doc_type}: {score}")
    
    # Assertions
    assert result['document_type'] == 'PAN', f"Expected PAN, got {result['document_type']}"
    assert result['confidence'] >= 0.5, f"Expected confidence >= 0.5, got {result['confidence']}"
    assert result['is_valid_kyc'] == True, "Should be valid KYC"
    
    print("\n✅ TEST PASSED: PAN Card correctly identified")
    return True


def test_passport():
    """Test Passport classification"""
    validator = DocumentValidator()
    
    # Sample Passport text
    passport_text = """
    PASSPORT
    Passport Number: A12345678
    Name: PASSPORT HOLDER
    Date of Birth: 05/06/1988
    Issued: 10/01/2015
    Valid Upto: 09/01/2025
    Place of Issue: NEW DELHI
    Republic of India
    """
    
    result = validator.validate_and_classify(passport_text)
    
    print("\n" + "=" * 60)
    print("TEST 4: Passport Classification")
    print("=" * 60)
    print(f"Document Type: {result['document_type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Is Valid KYC: {result['is_valid_kyc']}")
    print(f"Reason: {result['reason']}")
    print(f"\nAll Scores:")
    for doc_type, score in result['all_scores'].items():
        print(f"  {doc_type}: {score}")
    
    # Assertions
    assert result['document_type'] == 'Passport', f"Expected Passport, got {result['document_type']}"
    assert result['confidence'] >= 0.5, f"Expected confidence >= 0.5, got {result['confidence']}"
    assert result['is_valid_kyc'] == True, "Should be valid KYC"
    
    print("\n✅ TEST PASSED: Passport correctly identified")
    return True


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("DOCUMENT VALIDATOR TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_driving_license,
        test_aadhar,
        test_pan_card,
        test_passport
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

