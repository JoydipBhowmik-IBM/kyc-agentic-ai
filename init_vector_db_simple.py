#!/usr/bin/env python3
"""
Simple Vector Database Initialization Script (PAN-Only Edition)
Initializes KYC rules and fraud patterns for PAN documents only
"""

import json
import os
from pathlib import Path

def initialize_vector_db_simple():
    """Initialize vector database with PAN-only rules"""
    
    vector_db_path = "./kyc_vector_db"
    Path(vector_db_path).mkdir(parents=True, exist_ok=True)
    
    print("═══════════════════════════════════════════════════════")
    print("Initializing KYC Vector Database (PAN-ONLY RULES)")
    print("═══════════════════════════════════════════════════════")
    print(f"Vector DB Path: {vector_db_path}")
    
    # Create metadata directory structure
    metadata_dir = Path(vector_db_path) / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    # KYC Rules Data - PAN ONLY
    kyc_rules = [
        {
            "rule_id": "rule_001",
            "title": "PAN Document Verification",
            "description": "Permanent Account Number must contain 10 alphanumeric characters with specific format: AAAAA0000A",
            "document_type": "PAN",
            "country": "India",
            "requirement": "First 5 characters are letters, next 4 are digits, last is letter",
            "priority": "CRITICAL",
            "tags": ["pan", "india", "tax_id", "format_validation"]
        },
        {
            "rule_id": "rule_pan_photo",
            "title": "PAN Photo Requirement",
            "description": "PAN document must contain a clear photo/image of the cardholder",
            "document_type": "PAN",
            "country": "India",
            "requirement": "Document must contain a visible photograph for identity verification",
            "priority": "CRITICAL",
            "tags": ["pan", "india", "photo", "identity_verification"]
        },
        {
            "rule_id": "rule_pan_name",
            "title": "PAN Name Field Requirement",
            "description": "PAN must contain clearly readable name of the account holder",
            "document_type": "PAN",
            "country": "India",
            "requirement": "Full name must be clearly visible and match across all documents",
            "priority": "CRITICAL",
            "tags": ["pan", "india", "name_verification"]
        },
        {
            "rule_id": "rule_pan_dob",
            "title": "PAN Date of Birth Requirement",
            "description": "PAN document must contain date of birth information",
            "document_type": "PAN",
            "country": "India",
            "requirement": "Date of birth must be present and clearly readable",
            "priority": "HIGH",
            "tags": ["pan", "india", "age_verification"]
        },
        {
            "rule_id": "rule_pan_father_name",
            "title": "PAN Father's Name Requirement",
            "description": "PAN must contain father's name for identity cross-verification",
            "document_type": "PAN",
            "country": "India",
            "requirement": "Father's/Mother's name must be clearly visible on the document",
            "priority": "HIGH",
            "tags": ["pan", "india", "family_verification"]
        },
        {
            "rule_id": "rule_pan_signature",
            "title": "PAN Signature Requirement",
            "description": "PAN document must contain the signature of the account holder",
            "document_type": "PAN",
            "country": "India",
            "requirement": "Clear signature must be present on the document",
            "priority": "CRITICAL",
            "tags": ["pan", "india", "signature_verification", "authenticity"]
        },
        {
            "rule_id": "rule_pan_authenticity",
            "title": "PAN Authenticity Check",
            "description": "PAN document must pass authenticity and anti-spoofing checks",
            "document_type": "PAN",
            "country": "India",
            "requirement": "No signs of tampering, alteration, or forgery detected",
            "priority": "CRITICAL",
            "tags": ["pan", "india", "authenticity", "anti_fraud", "document_quality"]
        }
    ]
    
    # Fraud Patterns Data - PAN FOCUSED
    fraud_patterns = [
        {
            "pattern_id": "fraud_001",
            "pattern_name": "PAN Document Tampering",
            "description": "Signs of physical alteration, erasure, or modification in PAN document",
            "indicators": ["erasure_marks", "ink_inconsistency", "page_tears", "glue_residue", "overwritten", "altered"],
            "risk_level": "CRITICAL",
            "detection_method": "Visual inspection and metadata analysis of PAN image",
            "tags": ["pan", "document_fraud", "tampering", "forgery"]
        },
        {
            "pattern_id": "fraud_pan_002",
            "pattern_name": "PAN Identity Mismatch",
            "description": "Inconsistencies between PAN photo and user submission or biometric data",
            "indicators": ["face_mismatch", "different_facial_features", "age_discrepancy", "gender_mismatch"],
            "risk_level": "CRITICAL",
            "detection_method": "Facial recognition and biometric comparison with PAN photo",
            "tags": ["pan", "identity_fraud", "biometric_mismatch", "spoofing"]
        },
        {
            "pattern_id": "fraud_pan_003",
            "pattern_name": "PAN Duplicate/Synthetic Identity",
            "description": "Multiple PAN-based applications using similar documents with slight variations",
            "indicators": ["similar_photo", "pattern_in_variations", "network_fraud", "duplicate_pan"],
            "risk_level": "CRITICAL",
            "detection_method": "Database cross-referencing and PAN pattern analysis",
            "tags": ["pan", "synthetic_identity", "duplicate_application", "network_fraud"]
        },
        {
            "pattern_id": "fraud_pan_004",
            "pattern_name": "PAN Forged Signature",
            "description": "Signature on PAN appears to be forged or does not match known signature",
            "indicators": ["signature_inconsistency", "unnatural_signature", "stamp_mismatch", "forged_signature"],
            "risk_level": "HIGH",
            "detection_method": "Signature verification and historical comparison",
            "tags": ["pan", "signature_fraud", "forgery", "document_integrity"]
        },
        {
            "pattern_id": "fraud_pan_005",
            "pattern_name": "PAN Document Date Anomaly",
            "description": "PAN issue/validity dates that don't make logical sense",
            "indicators": ["future_issue_date", "invalid_validity", "reversed_dates", "impossible_dates"],
            "risk_level": "MEDIUM",
            "detection_method": "Date validation and temporal analysis of PAN",
            "tags": ["pan", "date_fraud", "temporal_anomaly", "document_integrity"]
        },
        {
            "pattern_id": "fraud_pan_006",
            "pattern_name": "PAN Photo Missing or Unclear",
            "description": "PAN document missing required photo or photo is not clear enough for verification",
            "indicators": ["missing_photo", "blurry_photo", "covered_face", "poor_quality_image"],
            "risk_level": "CRITICAL",
            "detection_method": "Image quality analysis and face detection",
            "tags": ["pan", "missing_photo", "image_quality", "verification_failure"]
        },
        {
            "pattern_id": "fraud_pan_007",
            "pattern_name": "PAN Information Inconsistency",
            "description": "Name, DOB, or other key information inconsistencies within PAN document",
            "indicators": ["name_mismatch", "dob_inconsistency", "field_mismatch", "conflicting_information"],
            "risk_level": "HIGH",
            "detection_method": "Cross-field validation and OCR comparison",
            "tags": ["pan", "data_inconsistency", "fraud_indicator", "field_validation"]
        },
        {
            "pattern_id": "fraud_pan_008",
            "pattern_name": "PAN Text Extraction Anomaly",
            "description": "OCR extraction returns garbled, invalid, or suspicious text from PAN",
            "indicators": ["invalid_pan_format", "garbled_text", "incomplete_extraction", "suspicious_characters"],
            "risk_level": "HIGH",
            "detection_method": "OCR quality check and regex validation",
            "tags": ["pan", "extraction_error", "document_quality", "fraud_indicator"]
        },
        {
            "pattern_id": "fraud_pan_009",
            "pattern_name": "PAN Watermark or Security Feature Tampering",
            "description": "Missing, altered, or suspicious watermarks or security features on PAN",
            "indicators": ["missing_watermark", "altered_security_feature", "fake_hologram", "removed_security_element"],
            "risk_level": "CRITICAL",
            "detection_method": "Visual inspection of security features and metadata analysis",
            "tags": ["pan", "security_compromise", "tampering", "authenticity_failure"]
        },
        {
            "pattern_id": "fraud_pan_010",
            "pattern_name": "PAN Known Fraudster Pattern",
            "description": "PAN matches known fraud ring patterns or appears in watchlist",
            "indicators": ["watchlist_match", "known_fraud_ring", "blacklisted_pan", "flagged_pattern"],
            "risk_level": "CRITICAL",
            "detection_method": "Database lookup and historical fraud pattern matching",
            "tags": ["pan", "watchlist", "fraud_ring", "known_fraudster"]
        }
    ]
    
    # Save KYC rules to JSON
    kyc_rules_file = Path(vector_db_path) / "kyc_rules.json"
    with open(kyc_rules_file, "w") as f:
        json.dump(kyc_rules, f, indent=2)
    print(f"✓ Saved {len(kyc_rules)} PAN-ONLY KYC rules to {kyc_rules_file}")
    
    # Save fraud patterns to JSON
    fraud_patterns_file = Path(vector_db_path) / "fraud_patterns.json"
    with open(fraud_patterns_file, "w") as f:
        json.dump(fraud_patterns, f, indent=2)
    print(f"✓ Saved {len(fraud_patterns)} PAN-FOCUSED fraud patterns to {fraud_patterns_file}")
    
    # Create index metadata
    index_metadata = {
        "version": "2.0",
        "edition": "PAN-ONLY",
        "created_at": "2026-04-04",
        "document_types_supported": ["PAN"],
        "collections": {
            "kyc_rules": {
                "count": len(kyc_rules),
                "file": "kyc_rules.json",
                "description": "PAN-only KYC validation rules"
            },
            "fraud_patterns": {
                "count": len(fraud_patterns),
                "file": "fraud_patterns.json",
                "description": "PAN-specific fraud detection patterns"
            }
        }
    }
    
    metadata_file = Path(vector_db_path) / "index.json"
    with open(metadata_file, "w") as f:
        json.dump(index_metadata, f, indent=2)
    
    print("═══════════════════════════════════════════════════════")
    print("Vector Database Initialization Complete!")
    print("═══════════════════════════════════════════════════════")
    print(f"✓ Edition: PAN-ONLY")
    print(f"✓ KYC Rules: {len(kyc_rules)} entries (PAN only)")
    print(f"✓ Fraud Patterns: {len(fraud_patterns)} entries (PAN-focused)")
    print(f"✓ Vector DB Location: {vector_db_path}")
    print(f"\nFiles created:")
    print(f"  - {kyc_rules_file}")
    print(f"  - {fraud_patterns_file}")
    print(f"  - {metadata_file}")

if __name__ == "__main__":
    initialize_vector_db_simple()
    print("\n✓ Vector database ready! (PAN-only edition)")


