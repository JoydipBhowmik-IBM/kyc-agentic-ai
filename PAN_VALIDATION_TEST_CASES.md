# PAN Card Validation - Test Examples

## Test Case 1: Valid PAN Card with All Required Fields

### Input Document:
```
GOVERNMENT OF INDIA
INCOME TAX DEPARTMENT
Permanent Account Number (PAN)
Name: Rajesh Kumar Singh
Father: Ram Kumar Singh  
Date of Birth: 15/03/1985
PAN: DXZPK1234A
Signature: [RAJESH KUMAR SINGH]
```

### Expected: ✓ APPROVED


## Test Case 2: REJECTED - Missing Government of India Tag

### Input Document:
```
Permanent Account Number (PAN) Card
Name: Priya Sharma
Date of Birth: 22/07/1990
PAN: AQZPL5678B
```

### Expected: ✗ REJECTED (CRITICAL: Missing Government of India tag)


## Test Case 3: REJECTED - Invalid PAN Format

### Input Document:
```
GOVERNMENT OF INDIA
INCOME TAX DEPARTMENT
Name: Amit Verma
Date of Birth: 11/05/1988
PAN: ABC123XYZ (INVALID FORMAT)
```

### Expected: ✗ REJECTED (Invalid PAN format)


## Test Case 4: REJECTED - Missing Date of Birth

### Input Document:
```
GOVERNMENT OF INDIA
INCOME TAX DEPARTMENT
Permanent Account Number (PAN)
Name: Neha Gupta
Father: Dr. Rajesh Gupta
PAN: GHIJL9012C
```

### Expected: ✗ REJECTED (Missing DOB)


## Test Case 5: REJECTED - Invalid DOB (Future Date)

### Input Document:
```
GOVERNMENT OF INDIA
INCOME TAX DEPARTMENT
Name: Sandeep Kumar
Date of Birth: 15/03/2025
PAN: MNOPQ3456D
```

### Expected: ✗ REJECTED (Year cannot be in future)


## Test Case 6: REJECTED - Watermarked Document

### Input Document:
```
SAMPLE - IMMIHELP.COM
GOVERNMENT OF INDIA
INCOME TAX DEPARTMENT
Name: Test User
Date of Birth: 01/01/1980
PAN: ABCDE0001F
```

### Expected: ✗ REJECTED (Watermark detected - Not original)


## Test Case 7: Valid PAN with OCR Variations

### Input Document:
```
GOVERNMENT OF INDIA
INCOME TAX DEPARTMENT
Name: Vikram Patel
Date of Birth: 30/12/1975
PAN: WXYZ1 A 0123 B  (with spaces)
```

### Expected: ✓ APPROVED (Spaces in PAN handled correctly)


## Test Case 8: Valid PAN with Hindi Government Text

### Input Document:
```
भारत सरकार
आयकर विभाग
Permanent Account Number (PAN)
Name: Deepak Verma
Date of Birth: 20/06/1993
PAN: HIJKL5678I
```

### Expected: ✓ APPROVED (Hindi "भारत सरकार" recognized)


## Critical Validation Rules

### MANDATORY Requirements:
1. **Government of India Tag** - MUST HAVE
2. **Valid PAN Format** - XXXXX0000X (MUST HAVE)
3. **Valid Date of Birth** - DD/MM/YYYY (MUST HAVE)

### Document REJECTED if ANY critical element is missing/invalid

---

## Running Tests

To test in production:

```bash
curl -X POST http://localhost:8007/extract \
  -F "file=@pan_card.jpg"
```

Check response for:
```json
{
  "is_valid_kyc": true,
  "document_type": "PAN",
  "extracted_patterns": {
    "government_of_india_tag": "Present",
    "pan_number": "XXXXX0000X",
    "date_of_birth": "DD/MM/YYYY",
    "dob_validation": "Valid"
  }
}
```
