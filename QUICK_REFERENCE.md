🚀 QUICK REFERENCE - KNOWLEDGE BASE CHANGES
════════════════════════════════════════════════════════════════════════════════

📌 WHAT WAS DONE:

1. Filtered KB to PAN-ONLY Rules
   - kyc_rules.json: 10 rules → 7 PAN-only rules
   - fraud_patterns.json: 10 generic → 10 PAN-specific patterns

2. Added Detailed Rule Validation Logging
   - Shows which rule is being checked
   - Shows PASS/FAIL for each rule
   - Shows rule priority and requirements
   - Summary of all passed/failed rules

3. Added MCP Server Verification
   - Logs when calling MCP server
   - Shows success/failure for each KB retrieval
   - Enhanced health check endpoint
   - Knowledge base status endpoint

4. Updated Initialization Script
   - Now creates PAN-only KB only
   - Updated metadata for version 2.0


🎯 WHAT TO TEST:

Test 1: Rule Validation Logging
────────────────────────────────
1. Process a PAN document through the system
2. Check verify-agent logs:
   docker logs kyc-verify-agent-1 | grep "RULE VALIDATION"
3. You should see:
   ✓ 🔍 RULE VALIDATION STARTED
   ✓ For each rule: ✅ PASSED or ❌ FAILED
   ✓ 📊 RULE VALIDATION SUMMARY


Test 2: MCP Knowledge Base Status
─────────────────────────────────
curl http://localhost:8003/health

You should see:
{
  "knowledge_base": {
    "status": "operational",      ← Should be "operational"
    "kyc_rules_available": true,  ← Should be true
    "fraud_patterns_available": true  ← Should be true
  }
}


Test 3: Full RAG Context Retrieval
──────────────────────────────────
1. Submit a PAN document for processing
2. Check reason-agent logs:
   docker logs kyc-reason-agent-1 | grep "RAG CONTEXT"
3. You should see:
   ✓ 🔍 RETRIEVING RAG CONTEXT...
   ✓ [Tool 1/3] KYC rules... ✅ SUCCESS - Retrieved 7
   ✓ [Tool 2/3] Fraud patterns... ✅ SUCCESS - Retrieved 10
   ✓ [Tool 3/3] Vector search... ✅ SUCCESS
   ✓ Knowledge Base Status: 🟢 OPERATIONAL


📊 FILES MODIFIED:

Core Knowledge Base:
  ✓ kyc_vector_db/kyc_rules.json (PAN-only)
  ✓ kyc_vector_db/fraud_patterns.json (PAN-focused)
  ✓ init_vector_db_simple.py (Updated for PAN-only)

Enhanced Logging:
  ✓ agents/verify-agent/main.py (Rule validation details)
  ✓ agents/reason-agent/main.py (MCP verification + health check)

Documentation:
  ✓ KNOWLEDGE_BASE_CHANGES.md (Complete summary)
  ✓ EXAMPLE_LOGS.md (Log examples)
  ✓ QUICK_REFERENCE.md (This file)


🔍 HOW TO VERIFY EVERYTHING WORKS:

Step 1: Restart all services
──────────────────────────────
docker-compose down
docker-compose up -d

Step 2: Check health endpoints
──────────────────────────────
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8010/health  # Orchestration
curl http://localhost:8008/health  # Verify Agent
curl http://localhost:8003/health  # Reason Agent ← Shows KB status

Step 3: Submit a test PAN
─────────────────────────
curl -X POST http://localhost:8000/kyc \
  -F "file=@pan_image.jpg"

Step 4: Watch the logs
──────────────────────
# In separate terminals:
docker logs kyc-verify-agent-1 -f
docker logs kyc-reason-agent-1 -f

Look for:
✓ "🔍 RULE VALIDATION STARTED"
✓ "📋 [Tool 1/3] Retrieving KYC rules"
✓ "Knowledge Base Status: 🟢 OPERATIONAL"


⚠️ TROUBLESHOOTING:

Problem: "Knowledge base Status: 🟡 PARTIAL"
Solution: 
  - Check if MCP server is running: docker logs kyc-mcp-server-1
  - Verify kyc_vector_db files exist and are not empty
  - Restart MCP server: docker-compose restart mcp-server

Problem: "Knowledge base Status: 🟠 ERROR"  
Solution:
  - MCP server is likely Down
  - docker-compose restart mcp-server
  - Check MCP logs: docker logs kyc-mcp-server-1

Problem: Rules not being checked
Solution:
  - kyc_vector_db/kyc_rules.json might be missing or empty
  - Run init_vector_db_simple.py to rebuild
  - Verify JSON is valid: python -m json.tool kyc_vector_db/kyc_rules.json

Problem: Logs don't show detailed rule validation
Solution:
  - Make sure Docker images are rebuilt
  - docker-compose down
  - docker-compose build
  - docker-compose up -d


📚 FILES CREATED:

Documentation:
  ✓ KNOWLEDGE_BASE_CHANGES.md - Complete change summary
  ✓ EXAMPLE_LOGS.md - Example log outputs
  ✓ QUICK_REFERENCE.md - This quick reference


🎓 KEY INSIGHTS:

Knowledge Base Now Contains:
  • 7 PAN-specific validation rules
  • 10 PAN-focused fraud patterns
  • Streamlined for PAN-only processing
  • Faster lookups and validation

Logging Improvements:
  • Each rule shows pass/fail status
  • MCP server calls are logged with results
  • Health check shows KB operational status
  • Easy to troubleshoot issues

Verification Flow:
  1. Extract Agent extracts text/metadata
  2. Verify Agent checks 7 PAN rules (logs each one)
  3. Verify Agent checks fraud patterns (logs matches)
  4. Reason Agent retrieves KB via MCP (logs retrieval)
  5. Reason Agent uses KB for AI analysis
  6. Risk/Decision agents make final decision


════════════════════════════════════════════════════════════════════════════════
