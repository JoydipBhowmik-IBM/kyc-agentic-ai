# Mock PAN Validation API - Quick Reference Card

## 🎯 What You Got

A complete **Mock PAN Validation API** with your PAN data (CYMPB5839A) that returns pre-defined validation responses for testing.

---

## ⚡ 30-Second Setup

```bash
# 1. Run tests
cd agents/verify-agent
python test_mock_validation.py

# 2. Start API service
python -m uvicorn mock_validation_endpoint:app --port 8001

# 3. Test it
curl "http://localhost:8001/test-cases"
```

---

## 🔥 Top 5 Endpoints

### 1. Validate Your PAN
```bash
curl -X POST "http://localhost:8001/validate-pan" \
  -H "Content-Type: application/json" \
  -d '{"pan_number": "CYMPB5839A", "name": "BORUGULA SURESH"}'
```
**Result:** `{"status": "APPROVED", "confidence": 0.98}`

### 2. Validate Multiple PANs
```bash
curl -X POST "http://localhost:8001/batch-validate" \
  -H "Content-Type: application/json" \
  -d '{"pan_list": ["CYMPB5839A", "SAMPLE123X", "ABCDE1234F"]}'
```

### 3. Get All Test Cases
```bash
curl "http://localhost:8001/test-cases"
```

### 4. Health Check
```bash
curl "http://localhost:8001/health"
```

### 5. Get Documentation
```bash
curl "http://localhost:8001/docs-mock"
```

---

## 📦 Test Cases Reference

| PAN | Status | Note |
|-----|--------|------|
| CYMPB5839A | ✅ APPROVED | Your original PAN - 98% confidence |
| ABCDE1234F | ✅ APPROVED | Generic valid - 95% confidence |
| BWZPS1234R | ❌ REJECTED | Different person (from attachment) |
| SAMPLE123X | ❌ REJECTED | Watermarked/sample document |
| INVALID123 | ❌ REJECTED | Invalid format |
| PHOTOCOPY01 | ❌ REJECTED | Photocopy detected |
| EXPIRY123A | ❌ REJECTED | Document expired |
| NOSIGN123C | ❌ REJECTED | Signature missing |
| NOPHOTO12D | ❌ REJECTED | Photo missing |
| LOWQUAL22E | ⚠️ WARNING | Low quality but readable |
| Any Other PAN | ❌ REJECTED | Not in pre-defined test cases |

---

## 💻 Python Usage

### Direct Import
```python
from mock_validation_api import MockPANValidator

validator = MockPANValidator()
result = validator.validate_pan("CYMPB5839A")

print(result['status'])       # APPROVED
print(result['confidence'])   # 0.98
print(result['name'])         # BORUGULA SURESH
```

### With Verify Agent
```python
from mock_validation_integration import VerifyAgentWithMockAPI

agent = VerifyAgentWithMockAPI(use_mock=True)
result = agent.verify_pan_with_mock({
    "pan_number": "CYMPB5839A",
    "name": "BORUGULA SURESH",
    "dob": "06/03/1992"
})

print(f"Status: {result['status']}")
```

### HTTP Request
```python
import requests

response = requests.post(
    "http://localhost:8001/validate-pan",
    json={"pan_number": "CYMPB5839A"}
)

result = response.json()
print(result['status'])  # APPROVED
```

---

## 🔄 Response Codes

```json
{
  "status": "APPROVED|REJECTED|PENDING|WARNING",
  "confidence": 0.0 - 1.0,
  "is_mock": true,
  "details": { ... }
}
```

| Status | Meaning | Example |
|--------|---------|---------|
| APPROVED | Valid PAN, can proceed | CYMPB5839A |
| REJECTED | Invalid/fraudulent | SAMPLE123X |
| PENDING | Valid format, needs real API | UNKNOWN1234Z |
| WARNING | Valid but proceed carefully | LOWQUAL22E |

---

## 📂 Files Created

```
agents/verify-agent/
├── mock_validation_api.py          ← Core validator
├── mock_validation_endpoint.py     ← FastAPI endpoints
├── mock_validation_integration.py  ← Integration examples
├── test_mock_validation.py         ← Tests
├── README_MOCK_API.md              ← This file
├── MOCK_API_GUIDE.md               ← Detailed guide
└── QUICK_REFERENCE.md              ← You are here!
```

---

## � STRICT MODE - Important!

**The mock API uses STRICT MODE:**

```
Only PANs in the pre-defined test cases return APPROVED
All other PANs (even with valid format) return REJECTED
```

### Example

```
✅ APPROVED:
   - CYMPB5839A (BORUGULA SURESH) ✓ In test cases
   - ABCDE1234F (JOHN DOE) ✓ In test cases

❌ REJECTED:
   - BWZPS1234R (TWITTERPREET SINGH) ✗ Not in test cases
   - UNKNOW1234Z ✗ Not in test cases
   - Any other valid format ✗ Not in test cases
```

This ensures **only your pre-defined test data gets approved**, preventing incorrect PANs from passing validation.

---

## 🎯 What Happens With Unknown PANs

### Test Your PAN
```python
from mock_validation_api import validate_pan_mock
result = validate_pan_mock("CYMPB5839A")
# Returns: APPROVED with 0.98 confidence
```

### Batch Test
```python
pans = ["CYMPB5839A", "SAMPLE123X", "ABCDE1234F"]
for pan in pans:
    result = validate_pan_mock(pan)
    print(f"{pan}: {result['status']}")
```

### Get Test Cases
```python
from mock_validation_api import get_mock_test_cases
cases = get_mock_test_cases()
for pan, status in cases.items():
    print(f"{pan} -> {status}")
```

### Use with Verify Agent
```python
# In verify-agent/main.py
from mock_validation_integration import VerifyAgentWithMockAPI

@app.post("/verify")
async def verify_pan(pan_data):
    agent = VerifyAgentWithMockAPI(use_mock=True)
    return agent.verify_pan_with_mock(pan_data)
```

---

## 🔌 Integration Methods

### Method 1: Direct Import (Simplest)
```python
from mock_validation_api import MockPANValidator
validator = MockPANValidator()
```

### Method 2: HTTP Request  
```python
requests.post("http://localhost:8001/validate-pan", json=data)
```

### Method 3: FastAPI Integration
```python
from mock_validation_endpoint import app
# Include in your FastAPI app
```

---

## ⚙️ Configuration

### Enable/Disable Mock API
```bash
# Use mock
export USE_MOCK_API=true

# Use real API
export USE_MOCK_API=false
```

### Custom Port
```bash
python -m uvicorn mock_validation_endpoint:app --port 9000
```

### Custom Host
```bash
python -m uvicorn mock_validation_endpoint:app --host 0.0.0.0 --port 8001
```

---

## 🧪 Testing

### Run All Tests
```bash
python test_mock_validation.py
```

### Run Specific Test
```bash
python -m pytest test_mock_validation.py::test_mock_validation_api -v
```

### Check Endpoints
```bash
curl -i "http://localhost:8001/health"
curl -i "http://localhost:8001/test-cases"
```

---

## 📊 Your PAN Data (Pre-loaded)

```
Document: PAN Card
Issuing Authority: Income Tax Department, Government of India

PAN Number: CYMPB5839A
Name: BORUGULA SURESH
Father's Name: BORUGULA MUNASWAMY
Date of Birth: 06/03/1992

Expected Result: APPROVED (Confidence: 0.98)
```

---

## ❓ FAQ

**Q: How do I use it?**
A: Run `python -m uvicorn mock_validation_endpoint:app --port 8001`, then send POST requests.

**Q: Can I add more test cases?**
A: Yes! Edit `mock_validation_api.py` and add to `_load_test_cases()` dictionary.

**Q: How do I switch to real API?**
A: Set `USE_MOCK_API=false` environment variable.

**Q: What format are responses?**
A: JSON with `status`, `confidence`, `is_mock`, and detailed `checks_passed`/`checks_failed`.

**Q: Does it work with Docker?**
A: Yes! Include the files in your Docker image and expose port 8001.

---

## 🎯 Implementation Checklist

- [ ] Copy files to `agents/verify-agent/`
- [ ] Run `python test_mock_validation.py`
- [ ] Start FastAPI: `python -m uvicorn mock_validation_endpoint:app --port 8001`
- [ ] Test endpoint: `curl "http://localhost:8001/test-cases"`
- [ ] Integrate with verify agent in main.py
- [ ] Test with your PAN: CYMPB5839A
- [ ] Switch to real API when ready

---

## 📚 Need More?

- **README_MOCK_API.md** → Full setup guide
- **MOCK_API_GUIDE.md** → Detailed documentation
- **mock_validation_api.py** → Source code
- **mock_validation_integration.py** → Integration patterns

---

**Status:** ✅ Ready to use!

Last Updated: April 2026
