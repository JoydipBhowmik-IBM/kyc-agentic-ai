#!/usr/bin/env python3
"""
Simple Vector Database Initialization Script
Initializes KYC rules and fraud patterns directly without external pip install
"""

import json
import os
from pathlib import Path

def initialize_vector_db_simple():
    """Initialize vector database with minimal dependencies"""
    
    vector_db_path = "./kyc_vector_db"
    Path(vector_db_path).mkdir(parents=True, exist_ok=True)
    
    print("═══════════════════════════════════════════════════════")
    print("Initializing KYC Vector Database")
    print("═══════════════════════════════════════════════════════")
    print(f"Vector DB Path: {vector_db_path}")
    
    # Create metadata directory structure
    metadata_dir = Path(vector_db_path) / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    # KYC Rules Data
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
            "rule_id": "rule_002",
            "title": "Aadhar Document Verification",
            "description": "Aadhar is a 12-digit unique identification number issued by UIDAI",
            "document_type": "Aadhar",
            "country": "India",
            "requirement": "Must be exactly 12 digits, numbers only",
            "priority": "CRITICAL",
            "tags": ["aadhar", "india", "biometric_id", "unique_identifier"]
        },
        {
            "rule_id": "rule_003",
            "title": "Passport Verification",
            "description": "International passport must be valid and contain biometric data",
            "document_type": "Passport",
            "country": "Global",
            "requirement": "Valid passport issued by recognized government authority",
            "priority": "CRITICAL",
            "tags": ["passport", "global", "travel_document", "biometric"]
        },
        {
            "rule_id": "rule_004",
            "title": "Driving License Verification",
            "description": "Valid driving license issued by motor vehicle authority",
            "document_type": "Driving License",
            "country": "India",
            "requirement": "Must contain DL number, issue date, and expiry date",
            "priority": "HIGH",
            "tags": ["driving_license", "india", "secondary_document"]
        },
        {
            "rule_id": "rule_005",
            "title": "Address Verification",
            "description": "Address must match across multiple documents during KYC verification",
            "document_type": "Multiple",
            "country": "Global",
            "requirement": "Consistent address information across all submitted documents",
            "priority": "CRITICAL",
            "tags": ["address", "verification", "consistency_check"]
        },
        {
            "rule_id": "rule_006",
            "title": "Date of Birth Validation",
            "description": "Date of birth must be consistent and fall within reasonable age range",
            "document_type": "Multiple",
            "country": "Global",
            "requirement": "DOB must be between 18-100 years old, consistent across docs",
            "priority": "HIGH",
            "tags": ["age_verification", "consistency", "document_matching"]
        },
        {
            "rule_id": "rule_007",
            "title": "Name Consistency Across Documents",
            "description": "Full name must match (or have acceptable variations) across all documents",
            "document_type": "Multiple",
            "country": "Global",
            "requirement": "Exact match or minor variations (middle name, suffix) acceptable",
            "priority": "CRITICAL",
            "tags": ["name_verification", "consistency_check", "document_matching"]
        },
        {
            "rule_id": "rule_008",
            "title": "Document Authenticity Check",
            "description": "Document must pass authenticity and anti-spoofing checks",
            "document_type": "Multiple",
            "country": "Global",
            "requirement": "No signs of tampering, alteration, or forgery detected",
            "priority": "CRITICAL",
            "tags": ["authenticity", "anti_fraud", "document_quality"]
        },
        {
            "rule_id": "rule_009",
            "title": "GST Registration Verification",
            "description": "GST registration number verification for businesses",
            "document_type": "GST Certificate",
            "country": "India",
            "requirement": "Valid 15-character alphanumeric GST number format",
            "priority": "HIGH",
            "tags": ["gst", "india", "business_verification", "tax_compliance"]
        },
        {
            "rule_id": "rule_010",
            "title": "Document Expiry Check",
            "description": "Ensure documents are not expired at the time of KYC",
            "document_type": "Multiple",
            "country": "Global",
            "requirement": "Expiry date must be in the future",
            "priority": "CRITICAL",
            "tags": ["expiry", "validity", "temporal_check"]
        }
    ]
    
    # Fraud Patterns Data
    fraud_patterns = [
        {
            "pattern_id": "fraud_001",
            "pattern_name": "Document Tampering",
            "description": "Signs of physical alteration, erasure, or modification in document",
            "indicators": ["erasure_marks", "ink_inconsistency", "page_tears", "glue_residue"],
            "risk_level": "CRITICAL",
            "detection_method": "Visual inspection and metadata analysis",
            "tags": ["document_fraud", "tampering", "forgery"]
        },
        {
            "pattern_id": "fraud_002",
            "pattern_name": "Identity Mismatch",
            "description": "Inconsistencies between document photo and biometric data",
            "indicators": ["face_mismatch", "different_facial_features", "age_discrepancy"],
            "risk_level": "CRITICAL",
            "detection_method": "Facial recognition and biometric comparison",
            "tags": ["identity_fraud", "biometric_mismatch", "spoofing"]
        },
        {
            "pattern_id": "fraud_003",
            "pattern_name": "Duplicate/Synthetic Identity",
            "description": "Multiple applications using similar documents with slight variations",
            "indicators": ["similar_photo", "pattern_in_variations", "network_fraud"],
            "risk_level": "HIGH",
            "detection_method": "Database cross-referencing and pattern analysis",
            "tags": ["synthetic_identity", "duplicate_application", "network_fraud"]
        },
        {
            "pattern_id": "fraud_004",
            "pattern_name": "PII Data Leakage Indicators",
            "description": "Presence of unredacted sensitive PII in documents",
            "indicators": ["full_account_numbers", "unmasked_ssn", "exposed_passwords"],
            "risk_level": "HIGH",
            "detection_method": "OCR and regex pattern matching",
            "tags": ["data_leakage", "pii_exposure", "security_risk"]
        },
        {
            "pattern_id": "fraud_005",
            "pattern_name": "Document Age Anomaly",
            "description": "Document issue/expiry dates that don't make logical sense",
            "indicators": ["future_issue_date", "invalid_expiry", "reversed_dates"],
            "risk_level": "MEDIUM",
            "detection_method": "Date validation and temporal analysis",
            "tags": ["date_fraud", "temporal_anomaly", "document_integrity"]
        },
        {
            "pattern_id": "fraud_006",
            "pattern_name": "Behavioral Red Flags",
            "description": "Unusual submission patterns suggesting automated fraud",
            "indicators": ["rapid_submissions", "vpn_usage", "multiple_devices", "unusual_location"],
            "risk_level": "MEDIUM",
            "detection_method": "Behavior analysis and metadata review",
            "tags": ["behavioral_fraud", "automation_risk", "suspicious_activity"]
        },
        {
            "pattern_id": "fraud_007",
            "pattern_name": "Known Fraudster Pattern",
            "description": "Matching known fraud ring patterns or watchlist entries",
            "indicators": ["watchlist_match", "known_fraud_ring", "blacklisted_id"],
            "risk_level": "CRITICAL",
            "detection_method": "Database lookup and pattern matching",
            "tags": ["watchlist", "fraud_ring", "known_fraudster"]
        },
        {
            "pattern_id": "fraud_008",
            "pattern_name": "Unusual Transaction Pattern",
            "description": "Transaction history showing suspicious money flow patterns",
            "indicators": ["sudden_large_transfers", "circular_transfers", "structured_deposits"],
            "risk_level": "HIGH",
            "detection_method": "Transaction analysis and correlation",
            "tags": ["transaction_fraud", "money_laundering", "suspicious_activity"]
        },
        {
            "pattern_id": "fraud_009",
            "pattern_name": "Geolocation Anomaly",
            "description": "Submission from unexpected geographic locations or impossible travel",
            "indicators": ["impossible_travel", "vpn_detected", "proxy_usage", "tor_usage"],
            "risk_level": "MEDIUM",
            "detection_method": "IP geolocation and travel time analysis",
            "tags": ["geolocation_fraud", "location_anomaly", "vpn_detection"]
        },
        {
            "pattern_id": "fraud_010",
            "pattern_name": "Device Fingerprint Inconsistency",
            "description": "Multiple submissions from same device with different identities",
            "indicators": ["same_device_id", "device_fingerprint_match", "shared_hardware"],
            "risk_level": "HIGH",
            "detection_method": "Device fingerprinting and cross-reference analysis",
            "tags": ["device_fraud", "identity_network", "shared_device"]
        }
    ]
    
    # Save KYC rules to JSON
    kyc_rules_file = Path(vector_db_path) / "kyc_rules.json"
    with open(kyc_rules_file, "w") as f:
        json.dump(kyc_rules, f, indent=2)
    print(f"✓ Saved {len(kyc_rules)} KYC rules to {kyc_rules_file}")
    
    # Save fraud patterns to JSON
    fraud_patterns_file = Path(vector_db_path) / "fraud_patterns.json"
    with open(fraud_patterns_file, "w") as f:
        json.dump(fraud_patterns, f, indent=2)
    print(f"✓ Saved {len(fraud_patterns)} fraud patterns to {fraud_patterns_file}")
    
    # Create index metadata
    index_metadata = {
        "version": "1.0",
        "created_at": "2026-03-28",
        "collections": {
            "kyc_rules": {
                "count": len(kyc_rules),
                "file": "kyc_rules.json"
            },
            "fraud_patterns": {
                "count": len(fraud_patterns),
                "file": "fraud_patterns.json"
            }
        }
    }
    
    metadata_file = Path(vector_db_path) / "index.json"
    with open(metadata_file, "w") as f:
        json.dump(index_metadata, f, indent=2)
    
    print("═══════════════════════════════════════════════════════")
    print("Vector Database Initialization Complete!")
    print("═══════════════════════════════════════════════════════")
    print(f"✓ KYC Rules: {len(kyc_rules)} entries")
    print(f"✓ Fraud Patterns: {len(fraud_patterns)} entries")
    print(f"✓ Vector DB Location: {vector_db_path}")
    print(f"\nFiles created:")
    print(f"  - {kyc_rules_file}")
    print(f"  - {fraud_patterns_file}")
    print(f"  - {metadata_file}")

if __name__ == "__main__":
    initialize_vector_db_simple()
    print("\n✓ Vector database ready!")

