from fastapi import FastAPI, UploadFile, File, HTTPException
import requests
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="KYC Orchestration Service", version="1.0.0")

# Configuration
EXTRACT_AGENT_URL = os.getenv("EXTRACT_AGENT_URL", "http://extract-agent:8000")
VERIFY_AGENT_URL = os.getenv("VERIFY_AGENT_URL", "http://verify-agent:8000")
REASON_AGENT_URL = os.getenv("REASON_AGENT_URL", "http://reason-agent:8000")
RISK_AGENT_URL = os.getenv("RISK_AGENT_URL", "http://risk-agent:8000")
DECISION_AGENT_URL = os.getenv("DECISION_AGENT_URL", "http://decision-agent:8000")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    agents = {}
    try:
        agents["extract"] = requests.get(f"{EXTRACT_AGENT_URL}/health", timeout=3).status_code == 200
    except:
        agents["extract"] = False

    try:
        agents["verify"] = requests.get(f"{VERIFY_AGENT_URL}/health", timeout=3).status_code == 200
    except:
        agents["verify"] = False

    try:
        agents["reason"] = requests.get(f"{REASON_AGENT_URL}/health", timeout=3).status_code == 200
    except:
        agents["reason"] = False

    try:
        agents["risk"] = requests.get(f"{RISK_AGENT_URL}/health", timeout=3).status_code == 200
    except:
        agents["risk"] = False

    try:
        agents["decision"] = requests.get(f"{DECISION_AGENT_URL}/health", timeout=3).status_code == 200
    except:
        agents["decision"] = False

    all_healthy = all(agents.values())
    return {"status": "healthy" if all_healthy else "degraded", "agents": agents}

async def call_agent(url: str, endpoint: str, data: Any = None, files: Any = None) -> Dict[str, Any]:
    """Helper function to call an agent with error handling"""
    try:
        if files:
            response = requests.post(f"{url}/{endpoint}", files=files, timeout=REQUEST_TIMEOUT)
        else:
            response = requests.post(f"{url}/{endpoint}", json=data, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            logger.error(f"Agent returned status {response.status_code}")
            return {"error": f"Agent error: {response.status_code}"}

        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout calling {url}/{endpoint}")
        return {"error": "Agent timeout"}
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error calling {url}/{endpoint}")
        return {"error": "Agent unavailable"}
    except Exception as e:
        logger.error(f"Error calling {url}/{endpoint}: {str(e)}")
        return {"error": str(e)}

@app.post("/process")
async def process(file: UploadFile = File(...)):
    """
    Orchestrate the KYC workflow through all agents
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        logger.info(f"Starting KYC workflow for file: {file.filename}")
        start_time = datetime.now()

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")

        workflow_data = {
            "filename": file.filename,
            "timestamp": datetime.now().isoformat(),
            "file_size": len(content)
        }

        # Step 1: Extract
        logger.info("Step 1: Extracting information from document...")
        extract_result = await call_agent(EXTRACT_AGENT_URL, "extract", files={"file": (file.filename, content)})
        workflow_data["extract"] = extract_result
        
        # DEBUG: Log extract result details
        logger.info(f"Extract Agent Response:")
        logger.info(f"  - status: {extract_result.get('status')}")
        logger.info(f"  - document_type: {extract_result.get('document_type')}")
        logger.info(f"  - confidence: {extract_result.get('confidence')}")
        logger.info(f"  - is_valid_kyc: {extract_result.get('is_valid_kyc')} ← CRITICAL FLAG")

        # Check if document type is unknown
        if extract_result.get("document_type") == "Unknown":
            logger.warning("❌ Document type identified as 'Unknown' - rejecting without calling other agents")
            workflow_data["final_status"] = "rejected"
            workflow_data["rejection_reason"] = "Document type is 'Unknown' - cannot process unknown or invalid documents. Please submit a valid KYC document (PAN, Aadhar, Passport, Driving License, Voter ID, Bank Statement, or Utility Bill)."
            workflow_data["document_type"] = "Unknown"
            workflow_data["confidence"] = extract_result.get('confidence', 0.0)
            # Set explicit rejected decision for unknown documents
            workflow_data["decision"] = {
                "status": "rejected",
                "decision": "REJECTED",
                "reason": workflow_data["rejection_reason"],
                "confidence": 1.0,
                "regulatory_action": "REJECT"
            }
            elapsed_time = (datetime.now() - start_time).total_seconds()
            workflow_data["processing_time_seconds"] = elapsed_time
            logger.info(f"Unknown document type - Workflow terminated in {elapsed_time}s")
            return workflow_data

        # Check if document is a valid KYC document
        if extract_result.get("status") == "invalid_document":
            logger.error(f"Invalid KYC document: {extract_result.get('reason')}")
            workflow_data["final_status"] = "rejected"
            workflow_data["rejection_reason"] = extract_result.get('reason')
            workflow_data["document_type"] = extract_result.get('document_type')
            workflow_data["confidence"] = extract_result.get('confidence')
            # Set explicit rejected decision for unknown/invalid documents
            workflow_data["decision"] = {
                "status": "rejected",
                "decision": "REJECTED",
                "reason": extract_result.get('reason', "Document is not a valid KYC document"),
                "confidence": 1.0,
                "regulatory_action": "REJECT"
            }
            elapsed_time = (datetime.now() - start_time).total_seconds()
            workflow_data["processing_time_seconds"] = elapsed_time
            logger.info(f"Document validation failed - Workflow terminated in {elapsed_time}s")
            return workflow_data

        if "error" in extract_result:
            logger.error(f"Extraction failed: {extract_result['error']}")
            workflow_data["final_status"] = "error"
            elapsed_time = (datetime.now() - start_time).total_seconds()
            workflow_data["processing_time_seconds"] = elapsed_time
            return workflow_data

        # Preserve document_type and confidence from extraction for successful documents
        if extract_result.get("document_type"):
            workflow_data["document_type"] = extract_result.get("document_type")
        if extract_result.get("confidence"):
            workflow_data["confidence"] = extract_result.get("confidence")

        # Step 2: Verify
        logger.info("Step 2: Verifying extracted information...")
        logger.info(f"  📋 Passing to Verify Agent:")
        logger.info(f"    - document_type: {extract_result.get('document_type')}")
        logger.info(f"    - is_valid_kyc: {extract_result.get('is_valid_kyc')} ← MUST PASS THIS!")
        logger.info(f"    - confidence: {extract_result.get('confidence')}")
        verify_result = await call_agent(VERIFY_AGENT_URL, "verify", data=extract_result)
        workflow_data["verify"] = verify_result
        
        # DEBUG: Log verify result
        logger.info(f"Verify Agent Response:")
        logger.info(f"  - verified: {verify_result.get('verified')}")
        logger.info(f"  - is_valid_kyc: {verify_result.get('is_valid_kyc')} ← MUST BE PASSED DOWNSTREAM")
        logger.info(f"  - document_type: {verify_result.get('document_type')}")
        logger.info(f"  - validations: {verify_result.get('validations')}")

        if "error" in verify_result:
            logger.error(f"Verification failed: {verify_result['error']}")

        # Check if verification failed - reject immediately
        if not verify_result.get("verified", True) or not verify_result.get("is_valid_kyc", True):
            logger.warning("❌ Verification failed - rejecting workflow")
            workflow_data["final_status"] = "rejected"
            workflow_data["rejection_reason"] = verify_result.get("reason", "Verification failed")
            workflow_data["document_type"] = verify_result.get("document_type", extract_result.get("document_type"))
            workflow_data["confidence"] = verify_result.get("confidence_score", 0.0)
            # Set explicit rejected decision
            workflow_data["decision"] = {
                "status": "rejected",
                "decision": "REJECTED",
                "reason": workflow_data["rejection_reason"],
                "confidence": 1.0,
                "regulatory_action": "REJECT"
            }
            elapsed_time = (datetime.now() - start_time).total_seconds()
            workflow_data["processing_time_seconds"] = elapsed_time
            logger.info(f"Verification failed - Workflow terminated in {elapsed_time}s")
            return workflow_data

        # Step 3: Reason (LLM Analysis)
        logger.info("Step 3: Performing LLM analysis...")
        logger.info(f"  📋 Document Type (passed to reason): {verify_result.get('document_type')}")
        logger.info(f"  📋 is_valid_kyc (passed to reason): {verify_result.get('is_valid_kyc')} ← CRITICAL")
        reason_result = await call_agent(REASON_AGENT_URL, "reason", data=verify_result)
        workflow_data["reason"] = reason_result
        
        logger.info(f"Reason Agent Response:")
        logger.info(f"  - is_valid_kyc: {reason_result.get('is_valid_kyc')} ← MUST CONTINUE")

        if "error" in reason_result:
            logger.error(f"Reasoning failed: {reason_result['error']}")
            logger.warning("Passing through verify result to risk agent")
            reason_result = verify_result

        # Step 4: Risk Assessment
        logger.info("Step 4: Assessing risk...")
        logger.info(f"  📋 Document Type (passed to risk): {reason_result.get('document_type')}")
        logger.info(f"  📋 is_valid_kyc (passed to risk): {reason_result.get('is_valid_kyc')} ← CRITICAL")
        risk_result = await call_agent(RISK_AGENT_URL, "risk", data=reason_result)
        workflow_data["risk"] = risk_result
        
        logger.info(f"Risk Agent Response:")
        logger.info(f"  - is_valid_kyc: {risk_result.get('is_valid_kyc')} ← MUST REACH DECISION")

        if "error" in risk_result:
            logger.error(f"Risk assessment failed: {risk_result['error']}")
            logger.warning("Passing through reason result to decision agent")
            risk_result = reason_result

        # Step 5: Decision
        logger.info("Step 5: Making final decision...")
        logger.info(f"  📋 Document Type (passed to decision): {risk_result.get('document_type')}")
        logger.info(f"  📋 is_valid_kyc (passed to decision): {risk_result.get('is_valid_kyc')} ← CRITICAL FOR APPROVAL")
        logger.info(f"  📋 verified (passed to decision): {risk_result.get('verified')}")
        logger.info(f"Sending to decision agent - risk_result keys: {risk_result.keys()}")
        logger.info(f"Risk result: {json.dumps({k: v for k, v in risk_result.items() if k not in ['text', 'analysis']}, indent=2)}")
        
        decision_result = await call_agent(DECISION_AGENT_URL, "decision", data=risk_result)
        
        logger.info(f"  📋 Document Type (returned from decision): {decision_result.get('document_type')}")
        logger.info(f"  📋 is_valid_kyc (returned from decision): {decision_result.get('is_valid_kyc')}")
        logger.info(f"Decision agent response: {json.dumps({k: v for k, v in decision_result.items() if k not in ['analysis', 'intelligence_metrics']}, indent=2)}")
        workflow_data["decision"] = decision_result

        if "error" in decision_result:
            logger.error(f"Decision failed: {decision_result['error']}")

        # Final verification: ensure document_type is at top level
        if not workflow_data.get("document_type"):
            if decision_result.get("document_type"):
                workflow_data["document_type"] = decision_result.get("document_type")
                logger.info(f"  ✅ Added document_type from decision: {workflow_data['document_type']}")
            elif risk_result.get("document_type"):
                workflow_data["document_type"] = risk_result.get("document_type")
                logger.info(f"  ✅ Added document_type from risk: {workflow_data['document_type']}")

        elapsed_time = (datetime.now() - start_time).total_seconds()
        workflow_data["processing_time_seconds"] = elapsed_time

        logger.info(f"KYC workflow completed in {elapsed_time}s")
        logger.info(f"📋 Final document_type in response: {workflow_data.get('document_type')}")
        return workflow_data

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8010"))
    uvicorn.run(app, host="0.0.0.0", port=port)
