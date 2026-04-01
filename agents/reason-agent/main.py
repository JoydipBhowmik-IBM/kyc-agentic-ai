"""
Enhanced Reason Agent with RAG + MCP Integration
Implements Retrieval Augmented Generation using Model Context Protocol
"""

from fastapi import FastAPI, HTTPException
import requests
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, List
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LangChain imports
try:
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.info("LangChain not available - basic analysis mode enabled")

from pydantic import BaseModel, Field

app = FastAPI(
    title="Reason Agent with RAG + MCP",
    version="3.0.0",
    description="Intelligent reasoning with Retrieval Augmented Generation and MCP tools"
)

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://mcp-server:8020")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))

# Initialize LLM
llm = None
if LANGCHAIN_AVAILABLE:
    try:
        llm = ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_URL,
            temperature=0.3,
            num_ctx=4096,  # Increased context window for RAG
        )
        logger.info(f"✓ LangChain ChatOllama initialized with model: {LLM_MODEL}")
    except Exception as e:
        logger.warning(f"Failed to initialize LangChain ChatOllama: {e}")
        llm = None

# ═══════════════════════════════════════════════════════════════
# PROMPT TEMPLATES WITH RAG CONTEXT
# ═══════════════════════════════════════════════════════════════

# Enhanced analysis prompt that includes retrieved context
rag_analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior KYC compliance expert with expertise in:
- Identity verification and fraud detection
- Regulatory compliance (AML/KYC requirements)
- Risk assessment and mitigation
- Document authenticity validation

You have access to:
- KYC Rules: Compliance requirements for different document types
- Fraud Patterns: Known fraud indicators and detection methods
- Historical Analysis: Previous analysis results for similar documents

Use all available context to provide comprehensive, evidence-based analysis."""),
    ("human", """Analyze this KYC document with the following context:

═════════════════════════════════════════════════════════════
DOCUMENT INFORMATION
═════════════════════════════════════════════════════════════
Document Type: {document_type}
Document Text:
{document_text}

Verification Status: {verification_status}
Confidence in Extraction: {confidence_score}

═════════════════════════════════════════════════════════════
RETRIEVED KYC RULES (from Vector DB)
═════════════════════════════════════════════════════════════
{kyc_rules_context}

═════════════════════════════════════════════════════════════
FRAUD PATTERNS TO CHECK (from Vector DB)
═════════════════════════════════════════════════════════════
{fraud_patterns_context}

═════════════════════════════════════════════════════════════
ANALYSIS TASK
═════════════════════════════════════════════════════════════
Provide comprehensive analysis in JSON format:
{{
    "summary": "Executive summary of analysis",
    "document_validity": true/false,
    "matches_kyc_rules": {{"matched": ["rule_ids"], "violations": ["rule_ids"]}},
    "fraud_risk_assessment": {{"patterns_detected": [], "risk_indicators": []}},
    "concerns": ["list", "of", "concerns"],
    "risk_indicators": ["specific", "risk", "signals"],
    "risk_level": "low|medium|high|critical",
    "confidence": 0.0-1.0,
    "recommendation": "Next recommended action",
    "reasoning": "Detailed reasoning for the assessment"
}}""")
])

# ═══════════════════════════════════════════════════════════════
# MCP CLIENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def call_mcp_tool(tool_name: str, query: str, document_type: str = None, top_k: int = 5) -> Dict[str, Any]:
    """
    Call MCP server tool to retrieve context
    
    Available tools:
    - retrieve_kyc_rules: Get relevant KYC rules
    - retrieve_fraud_patterns: Get fraud patterns to check
    - retrieve_from_vector_db: Generic vector DB search
    """
    try:
        url = f"{MCP_SERVER_URL}/{tool_name}"
        payload = {
            "query": query,
            "top_k": top_k
        }
        
        if document_type and tool_name == "retrieve_kyc_rules":
            payload["document_type"] = document_type
        
        logger.info(f"📡 Calling MCP tool: {tool_name} with query: '{query}'")
        
        response = requests.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"  ✓ {tool_name} returned {result.get('metadata', {}).get('results_count', 0)} results")
            return result
        else:
            logger.error(f"MCP tool error: {response.status_code}")
            return {
                "tool_name": tool_name,
                "status": "error",
                "results": [],
                "metadata": {"error": f"HTTP {response.status_code}"}
            }
    
    except requests.exceptions.Timeout:
        logger.error(f"MCP tool timeout: {tool_name}")
        return {
            "tool_name": tool_name,
            "status": "error",
            "results": [],
            "metadata": {"error": "Request timeout"}
        }
    except Exception as e:
        logger.error(f"MCP tool error: {str(e)}")
        return {
            "tool_name": tool_name,
            "status": "error",
            "results": [],
            "metadata": {"error": str(e)}
        }

def format_context(results: List[Dict[str, Any]]) -> str:
    """Format MCP results into readable context for LLM"""
    if not results or all(r.get("status") == "error" for r in results):
        return "No relevant context available from Vector DB"
    
    formatted = []
    for i, result in enumerate(results, 1):
        title = result.get("title") or result.get("pattern_name") or result.get("id", "Unknown")
        description = result.get("description") or result.get("content", "No description")
        formatted.append(f"{i}. {title}\n   {description}")
    
    return "\n".join(formatted)

async def retrieve_rag_context(document_type: str, document_text: str) -> Dict[str, str]:
    """
    Retrieve relevant context from Vector DB using MCP tools
    Implements RAG (Retrieval Augmented Generation)
    """
    logger.info("═══════════════════════════════════════════════════════")
    logger.info("🔍 Retrieving RAG Context from Vector DB")
    logger.info("═══════════════════════════════════════════════════════")
    
    context = {
        "kyc_rules": "",
        "fraud_patterns": "",
        "vector_db_search": ""
    }
    
    try:
        # MCP Tool 1: Retrieve relevant KYC rules
        logger.info(f"\n📋 Step 1: Retrieving KYC rules for {document_type}...")
        kyc_rules_result = await call_mcp_tool(
            "retrieve_kyc_rules",
            query=f"KYC requirements for {document_type}",
            document_type=document_type,
            top_k=5
        )
        
        if kyc_rules_result.get("status") == "success":
            context["kyc_rules"] = format_context(kyc_rules_result.get("results", []))
            logger.info(f"  ✓ Retrieved KYC rules")
        
        # MCP Tool 2: Retrieve fraud patterns
        logger.info("\n🚨 Step 2: Retrieving fraud patterns...")
        fraud_patterns_result = await call_mcp_tool(
            "retrieve_fraud_patterns",
            query=f"fraud patterns for document verification",
            top_k=5
        )
        
        if fraud_patterns_result.get("status") == "success":
            context["fraud_patterns"] = format_context(fraud_patterns_result.get("results", []))
            logger.info(f"  ✓ Retrieved fraud patterns")
        
        # MCP Tool 3: Generic Vector DB search based on document content
        logger.info("\n🔎 Step 3: Vector DB search for similar documents...")
        vector_search_result = await call_mcp_tool(
            "retrieve_from_vector_db",
            query=document_text[:500],  # Use first 500 chars of document
            top_k=3
        )
        
        if vector_search_result.get("status") == "success":
            context["vector_db_search"] = format_context(vector_search_result.get("results", []))
            logger.info(f"  ✓ Retrieved similar documents from vector DB")
        
        logger.info("\n✓ RAG context retrieval complete")
        
    except Exception as e:
        logger.error(f"Error retrieving RAG context: {e}")
    
    return context

async def perform_rag_enhanced_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform intelligent analysis using RAG + MCP with CONFLICT REASONING
    
    Reasoning-Driven Flow:
    1. Check if conflicts detected (mismatch found!)
    2. If conflicts: Retrieve relevant KYC rules about the conflict type
    3. If conflicts: Retrieve fraud patterns to check
    4. If conflicts: Use LLM to reason: "Is this fraud or explainable?"
    5. Make intelligent decision (not auto-reject)
    6. If no conflicts: Standard analysis
    
    Example: "Mismatch found, let me check KYC rules and fraud patterns before deciding"
    """
    
    text = data.get("text", "No text provided")
    verified = data.get("verified", False)
    confidence = data.get("confidence_score", 0.5)
    document_type = data.get("document_type", "Unknown")
    conflicts = data.get("conflicts", [])  # ← CONFLICTS FROM VERIFY AGENT
    
    logger.info("═══════════════════════════════════════════════════════")
    logger.info("🧠 Starting REASONING-DRIVEN Analysis with Conflict Detection")
    logger.info("═══════════════════════════════════════════════════════")
    
    # ═════════════════════════════════════════════════════════════
    # REASONING STEP 0: Check for Conflicts
    # ═════════════════════════════════════════════════════════════
    if conflicts and len(conflicts) > 0:
        logger.info(f"\n🚨 MISMATCH DETECTED! Found {len(conflicts)} conflict(s)")
        logger.info("🧠 Reasoning: 'Let me check rules and patterns before deciding...'")
        for conflict in conflicts:
            logger.info(f"  - {conflict.get('type', 'unknown')}: {conflict.get('description', 'N/A')}")
        
        # Before making a decision, retrieve specific context for THIS conflict type
        conflict_types = [c.get('type', 'unknown') for c in conflicts]
        conflict_query = ", ".join(conflict_types)
        
        logger.info(f"\n📋 Step 0A: Retrieving KYC rules for conflicts: {conflict_query}")
        conflict_rag_context = await retrieve_rag_context(
            f"Handling {conflict_query} conflicts",
            f"Document conflict types: {conflict_query}"
        )
        
        logger.info(f"✓ Retrieved context for conflict analysis")
    else:
        logger.info("\n✓ No conflicts detected - performing standard analysis")
        conflict_rag_context = None
    
    try:
        if not llm:
            return {
                "status": "error",
                "error": "LangChain LLM not initialized"
            }
        
        # STEP 0: Retrieve RAG context from Vector DB
        rag_context = await retrieve_rag_context(document_type, text)
        
        # ═════════════════════════════════════════════════════════════
        # REASONING STEP 1: Analyze Conflicts with LLM if they exist
        # ═════════════════════════════════════════════════════════════
        conflict_analysis = None
        if conflicts and len(conflicts) > 0 and llm:
            logger.info("\n🧠 Step 1: LLM Conflict Reasoning...")
            
            try:
                conflict_context = rag_context.get("kyc_rules", "No specific rules retrieved")
                fraud_context = rag_context.get("fraud_patterns", "No fraud patterns retrieved")
                
                # Create conflict analysis prompt
                conflict_prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a KYC compliance expert analyzing document conflicts.
Your task: Determine if conflicts are fraud indicators or explainable/resolvable issues.

Use provided context:
- KYC Rules: How document mismatches should be handled
- Fraud Patterns: Known fraud indicators to check against
- Document info: What we know about the document

Respond in JSON with:
{
    "conflicts_analysis": "Detailed analysis of each conflict",
    "fraud_risk": "low/medium/high - based on fraud patterns",
    "likely_cause": "What probably caused this conflict",
    "recommendation": "APPROVE/CONDITIONAL/ESCALATE/REJECT",
    "confidence": 0.0-1.0,
    "reasoning": "Why this recommendation"
}"""),
                    ("human", f"""Analyze these conflicts in the {document_type} document:

CONFLICTS DETECTED:
{json.dumps(conflicts, indent=2)}

KYC RULES CONTEXT:
{conflict_context[:1000]}

FRAUD PATTERNS:
{fraud_context[:1000]}

DOCUMENT CONTEXT:
- Type: {document_type}
- Verification Score: {verified}
- Confidence: {confidence}

Should we REJECT this document or is the conflict EXPLAINABLE?""")
                ])
                
                conflict_chain = conflict_prompt | llm | JsonOutputParser()
                conflict_analysis = conflict_chain.invoke({})
                
                logger.info(f"  ✓ Conflict analysis completed")
                logger.info(f"    - Fraud Risk: {conflict_analysis.get('fraud_risk')}")
                logger.info(f"    - Recommendation: {conflict_analysis.get('recommendation')}")
                logger.info(f"    - Reasoning: {conflict_analysis.get('reasoning', 'N/A')[:100]}...")
                
            except Exception as e:
                logger.warning(f"  ⚠️  Conflict analysis failed: {e}")
                conflict_analysis = None
        
        # STEP 2: Perform Standard LLM analysis with RAG context
        logger.info("\n📊 Step 2: LLM Analysis with RAG Context...")
        
        analysis_chain = rag_analysis_prompt | llm | JsonOutputParser()
        
        kyc_rules_formatted = rag_context.get("kyc_rules", "No rules retrieved")
        fraud_patterns_formatted = rag_context.get("fraud_patterns", "No patterns retrieved")
        
        llm_analysis = analysis_chain.invoke({
            "document_type": document_type,
            "document_text": text[:2000],
            "verification_status": "PASSED" if verified else "FAILED",
            "confidence_score": f"{confidence:.2f}",
            "kyc_rules_context": kyc_rules_formatted,
            "fraud_patterns_context": fraud_patterns_formatted
        })
        
        logger.info("  ✓ LLM analysis with RAG context completed")
        
        # STEP 2: Extract keywords
        logger.info("\n🔑 Step 2: Intelligent keyword extraction...")
        keyword_analysis = extract_keywords_with_intelligence(text)
        logger.info(f"  ✓ Found {keyword_analysis['total_keywords_found']} keywords")
        
        # STEP 3: Detect anomalies
        logger.info("\n⚠️  Step 3: Anomaly detection...")
        anomalies = detect_anomalies(text)
        total_anomalies = sum(len(v) for v in anomalies.values())
        logger.info(f"  ✓ Detected {total_anomalies} anomalies")
        
        # STEP 4: Calculate quality metrics
        logger.info("\n📈 Step 4: Document quality assessment...")
        quality_metrics = calculate_document_quality_metrics(text, confidence, keyword_analysis)
        logger.info(f"  ✓ Quality score: {quality_metrics['overall_quality_score']}")
        
        # Build comprehensive response
        enhanced_analysis = {
            "status": "success",
            "model": LLM_MODEL,
            "version": "3.1.0",  # Updated for conflict reasoning
            "langchain_enabled": True,
            "rag_enabled": True,
            "mcp_enabled": True,
            "reasoning_enabled": True,  # ← NEW: Reasoning-driven flag
            
            # Conflict Analysis (if conflicts detected)
            "conflict_analysis": conflict_analysis,  # ← NEW: LLM reasoning about conflicts
            "conflicts_detected": len(conflicts) > 0,  # ← NEW: Flag if conflicts
            "num_conflicts": len(conflicts),  # ← NEW: Count of conflicts
            
            # LLM Analysis with RAG
            "llm_analysis": llm_analysis,
            
            # RAG Context Details
            "rag_context": {
                "kyc_rules_retrieved": len(rag_context.get("kyc_rules", "").split("\n")),
                "fraud_patterns_retrieved": len(rag_context.get("fraud_patterns", "").split("\n")),
                "vector_db_results": len(rag_context.get("vector_db_search", "").split("\n"))
            },
            
            # Intelligence Metrics
            "intelligence_metrics": {
                "document_quality": quality_metrics,
                "keyword_analysis": keyword_analysis,
                "anomaly_detection": {
                    "total_anomalies": total_anomalies,
                    "by_category": anomalies
                }
            },
            
            # MCP Tool Execution
            "mcp_tools_used": [
                "retrieve_kyc_rules",
                "retrieve_fraud_patterns",
                "retrieve_from_vector_db"
            ],
            
            # Analysis Pipeline
            "analysis_pipeline": {
                "steps_completed": [
                    "conflict_detection",  # ← NEW: Conflict detection step
                    "conflict_reasoning" if conflict_analysis else "standard_analysis",  # ← NEW
                    "rag_context_retrieval",
                    "llm_analysis_with_rag",
                    "keyword_extraction",
                    "anomaly_detection",
                    "quality_assessment"
                ],
                "total_steps": 7 if conflict_analysis else 6,
                "enhancement_level": "RAG+MCP+CONFLICT_REASONING",  # ← NEW
                "reasoning_applied": conflict_analysis is not None  # ← NEW
            },
            
            "timestamp": datetime.now().isoformat()
        }
        
        # Preserve critical fields from input
        for field in ["document_type", "confidence", "is_valid_kyc", "all_scores", 
                      "reason", "filename", "verified", "confidence_score", "validations"]:
            if field in data:
                enhanced_analysis[field] = data[field]
        
        # Ensure is_valid_kyc is preserved
        if "is_valid_kyc" not in enhanced_analysis and "is_valid_kyc" in data:
            enhanced_analysis["is_valid_kyc"] = data["is_valid_kyc"]
        
        logger.info("═══════════════════════════════════════════════════════")
        logger.info("✓ RAG + MCP Enhanced Analysis Complete")
        logger.info("═══════════════════════════════════════════════════════")
        
        return enhanced_analysis
        
    except Exception as e:
        logger.error(f"Error in RAG enhanced analysis: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "fallback": True
        }

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def extract_keywords_with_intelligence(text: str) -> Dict[str, Any]:
    """Extract meaningful keywords and entities from document"""
    
    identity_keywords = [
        "name", "date of birth", "dob", "passport", "id", "identification",
        "address", "nationality", "country", "email", "phone"
    ]
    
    risk_keywords = [
        "suspicious", "high risk", "alert", "warning", "concerned",
        "unusual", "irregular", "discrepancy", "mismatch", "fraud"
    ]
    
    financial_keywords = [
        "account", "transaction", "transfer", "fund", "money",
        "balance", "credit", "debit", "wire", "investment"
    ]
    
    all_keywords = {
        "identity": identity_keywords,
        "risk": risk_keywords,
        "financial": financial_keywords
    }
    
    text_lower = text.lower()
    analysis = {}
    total_found = 0
    
    for category, keywords in all_keywords.items():
        found = [kw for kw in keywords if kw in text_lower]
        analysis[category] = {
            "keywords": found,
            "count": len(found),
            "coverage": len(found) / len(keywords) if keywords else 0
        }
        total_found += len(found)
    
    return {
        "by_category": analysis,
        "total_keywords_found": total_found,
        "keyword_richness": total_found / len(sum(all_keywords.values(), [])) if sum(all_keywords.values(), []) else 0,
        "has_identity_info": bool(analysis["identity"]["count"] > 0),
        "has_risk_indicators": bool(analysis["risk"]["count"] > 0),
        "has_financial_info": bool(analysis["financial"]["count"] > 0)
    }

def calculate_document_quality_metrics(text: str, confidence: float, keyword_analysis: Dict) -> Dict[str, float]:
    """Calculate comprehensive document quality metrics"""
    
    metrics = {}
    
    # Length metrics
    text_length = len(text)
    if text_length < 50:
        metrics["length_score"] = 0.0
    elif text_length < 200:
        metrics["length_score"] = 0.3
    elif text_length < 500:
        metrics["length_score"] = 0.6
    elif text_length < 2000:
        metrics["length_score"] = 0.85
    else:
        metrics["length_score"] = 1.0
    
    # Information completeness
    completeness = 0.0
    if keyword_analysis["has_identity_info"]:
        completeness += 0.3
    if keyword_analysis["has_risk_indicators"]:
        completeness += 0.3
    if keyword_analysis["has_financial_info"]:
        completeness += 0.4
    metrics["completeness_score"] = completeness
    
    # Keyword richness
    metrics["keyword_richness_score"] = min(keyword_analysis["keyword_richness"], 1.0)
    
    # Verification confidence
    metrics["verification_confidence"] = confidence
    
    # Overall quality
    weights = {
        "length_score": 0.20,
        "completeness_score": 0.30,
        "keyword_richness_score": 0.25,
        "verification_confidence": 0.25
    }
    
    overall_quality = sum(metrics[key] * weights[key] for key in weights.keys())
    metrics["overall_quality_score"] = round(overall_quality, 3)
    
    return metrics

def detect_anomalies(text: str) -> Dict[str, List[str]]:
    """Detect anomalies and suspicious patterns"""
    
    anomalies = {
        "missing_fields": [],
        "suspicious_patterns": [],
        "formatting_issues": [],
        "data_quality_issues": []
    }
    
    text_lower = text.lower()
    
    required_fields = ["name", "date", "address"]
    for field in required_fields:
        if field not in text_lower:
            anomalies["missing_fields"].append(field)
    
    suspicious_patterns = ["unknown", "n/a", "not provided"]
    for pattern in suspicious_patterns:
        if pattern in text_lower:
            anomalies["suspicious_patterns"].append(f"'{pattern}' found in document")
    
    lines = text.split("\n")
    if len(lines) < 3:
        anomalies["formatting_issues"].append("Very short document")
    
    return anomalies

# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check endpoint"""
    mcp_healthy = False
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=3)
        mcp_healthy = response.status_code == 200
    except:
        mcp_healthy = False
    
    return {
        "status": "healthy",
        "service": "reason-agent-rag",
        "version": "3.0.0",
        "mcp_server_connected": mcp_healthy
    }

@app.post("/reason")
async def reason(data: Dict[str, Any]):
    """
    Enhanced reasoning endpoint with RAG + MCP
    
    Features:
    - Retrieval Augmented Generation from Vector DB
    - Model Context Protocol integration
    - Multi-step LangChain analysis
    - Fraud pattern detection
    - KYC rule validation
    """
    try:
        logger.info("📨 Received reasoning request for analysis")
        
        # Use RAG-enhanced analysis
        result = await perform_rag_enhanced_analysis(data)
        
        return result

    except Exception as e:
        logger.error(f"Error in reason: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Advanced reasoning error: {str(e)}"
        )

@app.get("/capabilities")
async def capabilities():
    """Get capabilities of the enhanced reason agent"""
    return {
        "agent": "Reason Agent with RAG + MCP",
        "version": "3.0.0",
        "features": [
            "LangChain ChatOllama integration",
            "Retrieval Augmented Generation (RAG)",
            "Model Context Protocol (MCP) tools",
            "Vector DB integration (ChromaDB)",
            "Multi-step analysis chains",
            "Intelligent keyword extraction",
            "Fraud pattern detection",
            "KYC rule validation",
            "Document quality metrics",
            "Anomaly detection",
            "Comprehensive intelligence aggregation"
        ],
        "mcp_tools_available": [
            "retrieve_kyc_rules",
            "retrieve_fraud_patterns",
            "retrieve_from_vector_db"
        ],
        "analysis_steps": 5,
        "models_supported": [LLM_MODEL],
        "context_window": 4096,
        "rag_enabled": True
    }

@app.get("/mcp-status")
async def mcp_status():
    """Get MCP server status"""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            mcp_info = response.json()
            return {
                "status": "connected",
                "mcp_server": mcp_info,
                "reason_agent": "ready"
            }
    except:
        pass
    
    return {
        "status": "disconnected",
        "reason": "Cannot connect to MCP server",
        "mcp_url": MCP_SERVER_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

