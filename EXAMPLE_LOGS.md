📋 EXAMPLE LOG OUTPUTS - What You'll See Now
════════════════════════════════════════════════════════════════════════════════

1️⃣  VERIFY AGENT - DETAILED RULE VALIDATION LOGS
════════════════════════════════════════════════════════════════════════════════

When processing a PAN document, you'll see this in the logs:

----------------------------------------------------------------------
======================================================================
🔍 RULE VALIDATION STARTED - Document: pan
Total rules to check: 7
======================================================================

📌 Rule: rule_001 | Title: PAN Document Verification | Priority: CRITICAL
   Requirement: First 5 characters are letters, next 4 are digits, last is letter
   ✅ PASSED - Rule matched successfully

📌 Rule: rule_pan_photo | Title: PAN Photo Requirement | Priority: CRITICAL
   Requirement: Document must contain a visible photograph for identity verification
   ✅ PASSED - Rule matched successfully

📌 Rule: rule_pan_name | Title: PAN Name Field Requirement | Priority: CRITICAL
   Requirement: Full name must be clearly visible and match across all documents
   ✅ PASSED - Rule matched successfully

📌 Rule: rule_pan_dob | Title: PAN Date of Birth Requirement | Priority: HIGH
   Requirement: Date of birth must be present and clearly readable
   ✅ PASSED - Rule matched successfully

📌 Rule: rule_pan_father_name | Title: PAN Father's Name Requirement | Priority: HIGH
   Requirement: Father's/Mother's name must be clearly visible on the document
   ❌ FAILED - Text does not meet requirement: 'Father's/Mother's name must be clearly visible on the document'

📌 Rule: rule_pan_signature | Title: PAN Signature Requirement | Priority: CRITICAL
   Requirement: Clear signature must be present on the document
   ⚠️ No regex available for rule rule_pan_signature; skipping

📌 Rule: rule_pan_authenticity | Title: PAN Authenticity Check | Priority: CRITICAL
   Requirement: No signs of tampering, alteration, or forgery detected
   ✅ PASSED - Rule matched successfully

======================================================================
✅ RULE VALIDATION SUMMARY
   Passed Rules: 5 - ['rule_001', 'rule_pan_photo', 'rule_pan_name', 'rule_pan_dob', 'rule_pan_authenticity']
   Failed Rules: 1
      - rule_pan_father_name (HIGH): Father's/Mother's name must be clearly visible on the document
======================================================================
----------------------------------------------------------------------


2️⃣  FRAUD PATTERN CHECK LOGS
════════════════════════════════════════════════════════════════════════════════

----------------------------------------------------------------------
======================================================================
🚨 FRAUD PATTERN CHECK - Total patterns to verify: 10
======================================================================

🔎 Pattern: fraud_001 | PAN Document Tampering | Risk: CRITICAL
   Checking indicators: ['erasure_marks', 'ink_inconsistency', 'page_tears', 'glue_residue', 'overwritten', 'altered']
   ✅ OK - No indicators detected

🔎 Pattern: fraud_pan_002 | PAN Identity Mismatch | Risk: CRITICAL
   Checking indicators: ['face_mismatch', 'different_facial_features', 'age_discrepancy', 'gender_mismatch']
   ✅ OK - No indicators detected

🔎 Pattern: fraud_pan_003 | PAN Duplicate/Synthetic Identity | Risk: CRITICAL
   Checking indicators: ['similar_photo', 'pattern_in_variations', 'network_fraud', 'duplicate_pan']
   ⚠️ DETECTED - Matched indicators: ['network_fraud']

🔎 Pattern: fraud_pan_004 | PAN Forged Signature | Risk: HIGH
   Checking indicators: ['signature_inconsistency', 'unnatural_signature', 'stamp_mismatch', 'forged_signature']
   ✅ OK - No indicators detected

... [more patterns] ...

======================================================================
🚨 FRAUD CHECK RESULT: 1 pattern(s) detected!
   Overall Risk Level: CRITICAL
   - fraud_pan_003: PAN Duplicate/Synthetic Identity
======================================================================
----------------------------------------------------------------------


3️⃣  REASON AGENT - MCP SERVER & KNOWLEDGE BASE RETRIEVAL
════════════════════════════════════════════════════════════════════════════════

----------------------------------------------------------------------
======================================================================
🔍 RETRIEVING RAG CONTEXT FROM VECTOR DB (MCP SERVER)
======================================================================
MCP Server URL: http://mcp-server:8020
LLM Model: mistral
Document Type: PAN

📋 [Tool 1/3] Retrieving KYC rules for PAN...
   Query: 'KYC requirements for PAN'
   📡 Calling MCP tool: retrieve_kyc_rules with query: 'KYC requirements for PAN'
   ✅ SUCCESS - Retrieved 7 KYC rules
   Context length: 2451 chars

🚨 [Tool 2/3] Retrieving fraud patterns...
   Query: 'fraud patterns for document verification'
   📡 Calling MCP tool: retrieve_fraud_patterns with query: 'fraud patterns for document verification'
   ✅ SUCCESS - Retrieved 10 fraud patterns
   Context length: 8234 chars

🔎 [Tool 3/3] Vector DB search for similar documents...
   Query: Document text (first 500 chars)
   📡 Calling MCP tool: retrieve_from_vector_db with query: 'ABCDE1234FMASTER...'
   ✅ SUCCESS - Retrieved 5 similar documents
   Context length: 3421 chars

======================================================================
📊 RAG CONTEXT RETRIEVAL SUMMARY
======================================================================
KYC Rules Retrieved: 7 ✅
Fraud Patterns Retrieved: 10 ✅
Vector Search Results: 5 ✅

MCP Server Status: SUCCESS
Knowledge Base Status: 🟢 OPERATIONAL
======================================================================
----------------------------------------------------------------------


4️⃣  HEALTH CHECK ENDPOINT RESPONSE
════════════════════════════════════════════════════════════════════════════════

When you call: curl http://localhost:8003/health

Response when everything is working:
----------------------------------------------------------------------
{
  "status": "healthy",
  "service": "reason-agent-rag",
  "version": "3.1.0",
  "rag_enabled": true,
  "mcp_server": {
    "connected": true,
    "url": "http://mcp-server:8020",
    "error": null
  },
  "knowledge_base": {
    "status": "operational",
    "kyc_rules_available": true,
    "fraud_patterns_available": true
  },
  "llm": {
    "model": "mistral",
    "available": true
  }
}
----------------------------------------------------------------------

Response when MCP server is down:
----------------------------------------------------------------------
{
  "status": "degraded",
  "service": "reason-agent-rag",
  "version": "3.1.0",
  "rag_enabled": true,
  "mcp_server": {
    "connected": false,
    "url": "http://mcp-server:8020",
    "error": "Connection refused"
  },
  "knowledge_base": {
    "status": "error",
    "kyc_rules_available": false,
    "fraud_patterns_available": false
  },
  "llm": {
    "model": "mistral",
    "available": true
  }
}
----------------------------------------------------------------------

Response when knowledge base has no rules:
----------------------------------------------------------------------
{
  "status": "healthy",
  "service": "reason-agent-rag",
  "version": "3.1.0",
  "rag_enabled": true,
  "mcp_server": {
    "connected": true,
    "url": "http://mcp-server:8020",
    "error": null
  },
  "knowledge_base": {
    "status": "empty",
    "kyc_rules_available": false,
    "fraud_patterns_available": false
  },
  "llm": {
    "model": "mistral",
    "available": true
  }
}
----------------------------------------------------------------------


5️⃣  HOW TO CHECK IN YOUR DOCKER ENVIRONMENT
════════════════════════════════════════════════════════════════════════════════

Test 1: Check if rules are being validated correctly
────────────────────────────────────────────────
docker logs kyc-verify-agent-1 -f

You'll see:
✓ "🔍 RULE VALIDATION STARTED"
✓ For each rule: "✅ PASSED" or "❌ FAILED"
✓ "📊 RULE VALIDATION SUMMARY" with counts


Test 2: Check if MCP server is working
────────────────────────────────────────────────
curl http://localhost:8003/health | jq .mcp_server

Expected:
{
  "connected": true,
  "url": "http://mcp-server:8020",
  "error": null
}


Test 3: Check if knowledge base is operational
────────────────────────────────────────────────
curl http://localhost:8003/health | jq .knowledge_base

Expected:
{
  "status": "operational",
  "kyc_rules_available": true,
  "fraud_patterns_available": true
}


Test 4: Watch full reason agent logs with KB retrieval
────────────────────────────────────────────────────────
docker logs kyc-reason-agent-1 -f

You'll see:
✓ "🔍 RETRIEVING RAG CONTEXT FROM VECTOR DB"
✓ For each tool: "✅ SUCCESS" or "❌ FAILED"
✓ "📊 RAG CONTEXT RETRIEVAL SUMMARY"
✓ "Knowledge Base Status: 🟢 OPERATIONAL"


6️⃣  WHAT EACH LOG INDICATOR MEANS
════════════════════════════════════════════════════════════════════════════════

✅ PASSED/SUCCESS
   → Rule matched or tool retrieved data successfully
   → This is what you want to see

❌ FAILED
   → Rule did not match (this may still be OK if not CRITICAL)
   → Tool failed to retrieve data (check MCP server)

⚠️ WARNING
   → Something unexpected but not critical
   → Skipped a rule, partial KB retrieval, etc.

🚨 CRITICAL/ALARM
   → A critical rule failed or major issue detected
   → Document will be rejected
   → Check MCP server connectivity

🟢 OPERATIONAL
   → Knowledge base is working and serving data
   → All systems functional

🟡 PARTIAL
   → Some tools working, some not
   → Some rules/patterns available, but not all

🟠 ERROR
   → Major issue with knowledge base
   → MCP server down or knowledge base empty

════════════════════════════════════════════════════════════════════════════════
