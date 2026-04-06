# Mock PAN Validation API - Integration Guide

## Overview
The Mock PAN Validation API provides pre-defined validation responses for testing PAN verification without making external API calls. Use this during development and testing.

---

## Quick Start

### 1. **Test with Your PAN Data**

Your provided PAN details:
```
PAN Number: CYMPB5839A
Name: BORUGULA SURESH
Father's Name: BORUGULA MUNASWAMY
Date of Birth: 06/03/1992
```

### 2. **API Endpoints**

#### Endpoint 1: Single PAN Validation (POST)
```bash
curl -X POST "http://localhost:8001/validate-pan" \
  -H "Content-Type: application/json" \
  -d '{
    "pan_number": "CYMPB5839A",
    "name": "BORUGULA SURESH",
    "dob": "06/03/1992"
  }'
```

**Response:**
```json
{
  "pan_number": "CYMPB5839A",
  "name": "BORUGULA SURESH",
  "status": "APPROVED",
  "confidence": 0.98,
  "details": {
    "father_name": "BORUGULA MUNASWAMY",
    "dob": "06/03/1992",
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
    "is_original": true
  },
  "timestamp": "2024-01-15T10:30:45.123456",
  "is_mock": true
}
```

---

#### Endpoint 2: Batch Validation (POST)
```bash
curl -X POST "http://localhost:8001/batch-validate" \
  -H "Content-Type: application/json" \
  -d '{
    "pan_list": ["CYMPB5839A", "SAMPLE123X", "ABCDE1234F"]
  }'
```

**Response:**
```json
{
  "total": 3,
  "validated_at": "2024-01-15T10:31:20.456789",
  "validations": [
    {
      "pan_number": "CYMPB5839A",
      "status": "APPROVED",
      "confidence": 0.98
    },
    {
      "pan_number": "SAMPLE123X",
      "status": "REJECTED",
      "confidence": 0.02,
      "details": {
        "reason": "REJECTED - Document is a SAMPLE/WATERMARKED document"
      }
    },
    {
      "pan_number": "ABCDE1234F",
      "status": "APPROVED",
      "confidence": 0.95
    }
  ],
  "summary": {
    "approved": 2,
    "rejected": 1,
    "pending": 0,
    "approval_rate": "66.7%"
  }
}
```

---

#### Endpoint 3: Get All Test Cases (GET)
```bash
curl "http://localhost:8001/test-cases"
```

**Response:**
```json
{
  "total_test_cases": 10,
  "test_cases": {
    "CYMPB5839A": "APPROVED",
    "ABCDE1234F": "APPROVED",
    "SAMPLE123X": "REJECTED",
    "INVALID123": "REJECTED",
    "PHOTOCOPY01": "REJECTED",
    "EXPIRY123A": "REJECTED",
    "NOSIGN123C": "REJECTED",
    "NOPHOTO12D": "REJECTED",
    "LOWQUAL22E": "WARNING"
  }
}
```

---

## Available Test Cases

### ✅ APPROVED (Valid PANs)
```
CYMPB5839A  → Your provided PAN data (Confidence: 0.98)
ABCDE1234F  → Generic valid PAN (Confidence: 0.95)
```

### ❌ REJECTED (Invalid PANs)
```
BWZPS1234R   → TWITTERPREET SINGH (Different person - not in approved list)
SAMPLE123X   → Watermarked/Sample document (for demonstration)
INVALID123   → Invalid format (doesn't match XXXXX0000X)
PHOTOCOPY01  → Detected as photocopy (not original)
EXPIRY123A   → Document expired or cancelled
NOSIGN123C   → Signature field missing
NOPHOTO12D   → Photo field missing
```

### ⚠️ WARNING (Caution)
```
LOWQUAL22E   → Low quality but readable (Manual verification recommended)
```

### 🔒 STRICT MODE
```
Any Unknown PAN → REJECTED (even with valid XXXXX0000X format)
```

**IMPORTANT:** The mock API operates in STRICT MODE:
- ✅ Only PANs in the pre-defined test cases are APPROVED
- ❌ All other PANs (including valid formats) are REJECTED
- This ensures your test data validation is strict and controlled

---

## Integration with Verify Agent

### Option 1: Use as External Service

Update `verify-agent/main.py`:

```python
import requests
from mock_validation_endpoint import app

# Call mock validation API
def validate_with_mock(pan_data):
    """Validate PAN using mock API"""
    response = requests.post(
        "http://localhost:8001/validate-pan",
        json={
            "pan_number": pan_data["pan_number"],
            "name": pan_data.get("name"),
            "dob": pan_data.get("dob")
        }
    )
    return response.json()

# Usage in verification flow
pan_validation = validate_with_mock({
    "pan_number": "CYMPB5839A",
    "name": "BORUGULA SURESH",
    "dob": "06/03/1992"
})

print(f"Status: {pan_validation['status']}")
print(f"Confidence: {pan_validation['confidence']}")
```

### Option 2: Direct Import

In `verify-agent/main.py`:

```python
from mock_validation_api import MockPANValidator

# Initialize
validator = MockPANValidator()

# Validate
result = validator.validate_pan(
    pan_number="CYMPB5839A",
    name="BORUGULA SURESH"
)

print(f"Validation Result: {result['status']}")
```

### Option 3: Run as Separate Service

```bash
# Terminal 1: Start mock API service
cd agents/verify-agent
python -m uvicorn mock_validation_endpoint:app --host 0.0.0.0 --port 8001

# Terminal 2: Use it from verify agent
# Call: http://localhost:8001/validate-pan (with JSON body)
```

---

## Docker Integration

### Dockerfile for Mock Validation Service

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY mock_validation_api.py .
COPY mock_validation_endpoint.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "mock_validation_endpoint:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Docker Compose Integration

```yaml
mock-validator:
  build:
    context: ./agents/verify-agent
    dockerfile: Dockerfile.mock
  ports:
    - "8001:8001"
  environment:
    - LOG_LEVEL=INFO
  networks:
    - kyc-network
```

---

## Python Usage Examples

### Example 1: Validate Single PAN
```python
from mock_validation_api import validate_pan_mock

# Validate your PAN
result = validate_pan_mock("CYMPB5839A", name="BORUGULA SURESH")

print(f"PAN: {result['pan_number']}")
print(f"Status: {result['status']}")
print(f"Confidence: {result['confidence']}")
print(f"Name: {result['name']}")
print(f"Fraud Score: {result['details']['fraud_score']}")
```

### Example 2: Batch Validation
```python
from mock_validation_api import MockPANValidator

validator = MockPANValidator()

pans = ["CYMPB5839A", "SAMPLE123X", "INVALID123"]
results = validator.batch_validate_pans(pans)

for validation in results["validations"]:
    print(f"{validation['pan_number']}: {validation['status']}")

print(f"Approval Rate: {results['summary']['approval_rate']}")
```

### Example 3: Check Available Test Cases
```python
from mock_validation_api import get_mock_test_cases

test_cases = get_mock_test_cases()
for pan, status in test_cases.items():
    print(f"{pan:<15} → {status}")
```

---

## Response Structure

All validation responses follow this structure:

```json
{
  "pan_number": "CYMPB5839A",
  "name": "BORUGULA SURESH",
  "status": "APPROVED|REJECTED|PENDING|WARNING",
  "confidence": 0.98,
  "is_mock": true,
  "timestamp": "2024-01-15T10:30:45.123456",
  "details": {
    "father_name": "BORUGULA MUNASWAMY",
    "dob": "06/03/1992",
    "reason": "Detailed reason for the decision",
    "checks_passed": ["List of passed validation checks"],
    "checks_failed": ["List of failed validation checks"],
    "warnings": ["Any warnings if status is WARNING"],
    "fraud_score": 0.0,
    "is_original": true,
    "is_sample": false,
    "is_photocopy": false,
    "is_expired": false
  }
}
```

---

## Switching Between Mock and Real APIs

### Configuration in Verify Agent

```python
import os

USE_MOCK_API = os.getenv("USE_MOCK_API", "true").lower() == "true"

def get_validator():
    if USE_MOCK_API:
        from mock_validation_api import MockPANValidator
        return MockPANValidator()
    else:
        # Use real validation API
        return RealPANValidator()
```

### Runtime Switch

```bash
# Use Mock API
export USE_MOCK_API=true
python verify-agent/main.py

# Use Real API
export USE_MOCK_API=false
python verify-agent/main.py
```

---

## Testing Guide

### Test All Scenarios

```bash
# Run tests
python -m pytest test_mock_validation.py -v

# Test specific case
python -m pytest test_mock_validation.py::test_approved_pan -v
```

### Manual Testing

```bash
# Test 1: Valid PAN
curl -X POST "http://localhost:8001/validate-pan" \
  -H "Content-Type: application/json" \
  -d '{"pan_number": "CYMPB5839A"}'

# Test 2: Watermarked PAN
curl -X POST "http://localhost:8001/validate-pan" \
  -H "Content-Type: application/json" \
  -d '{"pan_number": "SAMPLE123X"}'

# Test 3: Invalid Format
curl -X POST "http://localhost:8001/validate-pan" \
  -H "Content-Type: application/json" \
  -d '{"pan_number": "INVALID123"}'
```

---

## Benefits

✅ **Fast Testing** - No external API calls, instant responses  
✅ **Consistent** - Same results for same input every time  
✅ **Offline** - Works without internet connection  
✅ **Comprehensive** - Test both success and failure cases  
✅ **Easy Integration** - Works with existing verify agent  
✅ **Real Data** - Uses your actual PAN for testing  

---

## Next Steps

1. ✅ Copy `mock_validation_api.py` to `agents/verify-agent/`
2. ✅ Copy `mock_validation_endpoint.py` to `agents/verify-agent/`
3. 🔄 Update `agents/verify-agent/main.py` to use mock validator
4. 🧪 Test with your PAN: `CYMPB5839A`
5. 🚀 Switch to real API when ready

---

## Questions?

All responses include `"is_mock": true` so you can distinguish mock from real API calls.
