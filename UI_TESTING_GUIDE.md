# 🧪 KYC System Testing Checklist - What to Test from UI

> **You asked:** "I just can test from UI" - Here's exactly what to do and look for!

---

## ✅ Quick Setup (Do This First)

### If Using Docker:
```powershell
cd "c:\kyc latest\kyc-agentic-ai"
docker-compose up -d --build
# Wait 30 seconds for all containers to start
```

### If Running Locally:
1. Ensure API is running on `http://localhost:8000`
2. Ensure Frontend is running on `http://localhost:3000`
3. Open browser: `http://localhost:3000`

---

## 🎯 Test 1: Valid PAN Document (Should PASS)

**What to do:**
1. Open UI at http://localhost:3000
2. Click "Select Document" 
3. Upload a **valid, clear PAN document image**
4. Click "Submit for Processing"

**What you should see:**
- ✅ Document Type: **PAN** (with confidence %)
- ✅ NO red warning box (no failed rules)
- ✅ Final Decision: **APPROVED** (green text)
- ✅ Processing time shown (e.g., 8.5 seconds)

**If you see something else → There's a problem ❌**

---

## ⚠️ Test 2: Invalid/Damaged PAN Document (Should FAIL + Show which rule failed)

**What to do:**
1. Find a PAN image that is:
   - Blurry or poorly scanned
   - Missing signature
   - Missing name field
   - Missing date of birth
2. Upload it
3. Click "Submit for Processing"

**What you should see:**
- ✅ Document Type: **PAN**
- ✅ **RED BOX: "⚠️ KYC Rules Violated"** 
- ✅ **Shows exactly which rule failed**, for example:
  ```
  ❌ rule_pan_signature: PAN Signature (Priority: CRITICAL)
  Requirement: Clear, visible signature on document
  Why Failed: Signature missing or unclear
  ```
- ✅ Final Decision: **REJECTED** (red text)

**THIS IS THE NEW FEATURE!** 🎉 Before, you couldn't see which rule failed. Now it's visible!

---

## 🚫 Test 3: Unknown/Non-Document Image (Should FAIL immediately)

**What to do:**
1. Upload any **random image** (photo, landscape, etc.) - NOT a KYC document
2. Click "Submit"

**What you should see:**
- ⚠️ Document Type: **Unknown** (in yellow box)
- ✅ Final Decision: **REJECTED**
- ✅ Rejection Reason: "Document type is 'Unknown' - cannot process"
- ✅ Processing should be fast (1-2 seconds) - rejected early!

---

## 📊 Test 4: Processing Steps Display

**While document is being processed, you should see:**

```
Processing Steps:
1️⃣ ✓ Extract Agent          [Complete in 2.00s]
2️⃣ ✓ Verify Agent            [Complete in 2.00s]  ← SHOWS FAILED RULES HERE
3️⃣ ⏳ Reason Agent (RAG+MCP)  [Processing...]
4️⃣ ⏳ Risk Agent              [Waiting...]
5️⃣ ⏳ Decision Agent          [Waiting...]
```

**All 5 steps should go green (✓) if document passes all checks**

---

## 🔍 Detailed Results Section (This is NEW!)

**After processing completes, scroll down to see:**

### Section 1: Document Type (Green Box)
```
📋 Document Type Identified: PAN
Document Identification Confidence: 95.2%
```

### Section 2: **⭐ KYC Rules Violated (NEW!)** - Red Box
```
⚠️ KYC RULES VIOLATED
X rule(s) failed validation:

❌ rule_id: Rule Name (Priority)
   Requirement: What the rule needs
   Why Failed: Specific reason it failed
```

### Section 3: Final Decision
```
Final Decision: APPROVED or REJECTED
Decision Confidence: XX%
```

### Section 4: Risk Assessment
```
Risk Assessment: LOW/MEDIUM/HIGH
Score: 0.xxx
```

### Section 5: Timestamps
```
Total Processing Time: X.X seconds
Processed At: 2026-04-05 10:30 AM
```

---

## ⚙️ What Each Agent Does (You'll See in Steps)

| Agent | What It Does | What User Sees |
|-------|-------------|-----------------|
| **Extract** | Reads document image, extracts text | Document Type, Confidence % |
| **Verify** | Checks against KYC rules | **NOW SHOWS FAILED RULES!** ⭐ |
| **Reason** | AI analysis + knowledge retrieval | Analysis results |
| **Risk** | Calculates risk score | Risk Level (LOW/MED/HIGH) |
| **Decision** | Makes final APPROVED/REJECTED call | Final Decision |

---

## 🎯 What the Lead Asked For

Your lead said:
> "If compliances not working we can remove it... also I am not seeing which kyc rule violating in ui"

**Status:** ✅ DONE!
- ✅ Removed non-working "compliance" references from UI
- ✅ **NOW SHOWS WHICH KYC RULE IS VIOLATING** - This is what we added!

---

## Common Issues & Fix

### Issue 1: "I uploaded a document but nothing happened"
- **Fix:** Wait 10+ seconds - processing takes time
- **Check:** Look at the 5 processing steps changing status

### Issue 2: "I see processing steps but no results"
- **Fix:** Scroll down - results appear below the steps
- **Check:** Results start appearing after "decision" step completes

### Issue 3: "I don't see the 'KYC Rules Violated' section"
- **Fix:** This only appears if rules FAILED
- **Test:** Try uploading an invalid/damaged document
- **Valid documents won't show failed rules** (that's correct!)

### Issue 4: "Browser shows old UI without rule violations"
- **Fix:** Clear browser cache: **Ctrl+F5** (hard refresh)
- **Or:** Open in Private/Incognito window

---

## Summary Table - Know What to Expect

| Test | Input | Expected Output | Status |
|------|-------|-----------------|--------|
| Valid PAN | Good quality PAN image | APPROVED, no failed rules | ✅ Works |
| Invalid PAN | Blurry/damaged PAN | REJECTED, shows which rule(s) failed | ✅ **NEW** |
| Non-document | Random photo | REJECTED, "Unknown" type | ✅ Works |
| Processing | Any valid input | 5-step progress display | ✅ Works |
| Failed Rules | Any failed validation | RED BOX showing rule details | ✅ **NEW** |

---

## 🚀 Next: How to Report Results

When testing is complete, tell us:

1. ✅ **What worked?** (Valid documents approved? Failed rules shown clearly?)
2. ❌ **What didn't work?** (If any test fails)
3. 💭 **Any feedback?** (UI clear? Easy to understand? Need anything else?)

---

## Quick Reference: URLs

| Service | URL |
|---------|-----|
| Frontend (UI) | `http://localhost:3000` |
| API Gateway | `http://localhost:8000` |
| Orchestration Service | `http://localhost:8000/process` |
| MCP Server | `http://localhost:8020` |

---

**Ready to test? Go to http://localhost:3000 and upload a PAN document!** 🎯
