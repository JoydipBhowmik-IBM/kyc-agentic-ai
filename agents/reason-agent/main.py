from fastapi import FastAPI, HTTPException
import requests
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, List
import numpy as np

# Configure logging first before using it
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═════════════════════════════════════════════════════════════
# LANGCHAIN IMPORTS - Advanced AI capabilities
# (Optional - functionality gracefully degrades if not available)
# ═════════════════════════════════════════════════════════════
try:
    from langchain_ollama import ChatOllama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.info("LangChain not available - basic analysis mode enabled")

try:
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
except ImportError:
    try:
        from langchain.prompts import ChatPromptTemplate, PromptTemplate
        from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    except ImportError:
        LANGCHAIN_AVAILABLE = False

try:
    from langchain.chains import LLMChain, SequentialChain
except ImportError:
    LLMChain = None
    SequentialChain = None
    
try:
    from langchain.schema import Document
except ImportError:
    try:
        from langchain_core.documents import Document
    except ImportError:
        Document = None
    
from pydantic import BaseModel, Field


app = FastAPI(title="Reason Agent with Advanced LangChain", version="2.0.0")

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))

# ═════════════════════════════════════════════════════════════
# LANGCHAIN LLM INITIALIZATION (Optional)
# ═════════════════════════════════════════════════════════════
llm = None
if LANGCHAIN_AVAILABLE:
    try:
        llm = ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_URL,
            temperature=0.3,
            num_ctx=2048,  # Larger context window for better analysis
        )
        logger.info(f"LangChain ChatOllama initialized with model: {LLM_MODEL}")
    except Exception as e:
        logger.warning(f"Failed to initialize LangChain ChatOllama: {e}")
        llm = None
else:
    logger.info("LangChain not available - LLM features disabled")

# ═════════════════════════════════════════════════════════════
# PROMPT TEMPLATES - Reusable, structured prompts
# ═════════════════════════════════════════════════════════════

# Template 1: Comprehensive document analysis
analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a senior KYC (Know Your Customer) compliance expert with expertise in:
- Identity verification and fraud detection
- Regulatory compliance (AML/KYC requirements)
- Risk assessment and mitigation
- Document authenticity validation

Analyze KYC documents with precision and provide actionable insights."""),
    ("human", """Analyze this KYC document:

Document Text:
{document_text}

Verification Status: {verification_status}
Confidence in Extraction: {confidence_score}

Provide a detailed analysis in JSON format:
{{
    "summary": "Executive summary of analysis",
    "identity_verified": true/false,
    "concerns": ["list", "of", "concerns"],
    "risk_indicators": ["specific", "risk", "signals"],
    "risk_level": "low|medium|high",
    "flags_detected": {{"fraud": [], "suspicious": [], "incomplete": []}},
    "recommendation": "Recommended next action",
    "confidence": 0.0-1.0
}}""")
])

# Template 2: Risk factor extraction
risk_factors_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a risk analyst. Extract and categorize risk factors from the KYC analysis.
Categorize by: IDENTITY, DOCUMENTATION, BEHAVIORAL, REGULATORY, OTHER"""),
    ("human", """Extract risk factors from this analysis:

{analysis_text}

Return JSON:
{{
    "risk_factor_count": number,
    "categorized_factors": {{}},
    "severity_breakdown": {{"critical": 0, "high": 0, "medium": 0, "low": 0}}
}}""")
])

# Template 3: Confidence and completeness assessment
confidence_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a quality assurance expert assessing analysis reliability."),
    ("human", """Rate the analysis confidence:

Document Quality: {document_text}
Analysis Provided: {analysis_text}

Return JSON:
{{
    "overall_confidence": 0.0-1.0,
    "reason": "why this confidence level",
    "missing_information": ["list", "of", "gaps"],
    "data_quality_score": 0.0-1.0
}}""")
])

# Template 4: Multi-angle risk scoring
multi_angle_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at multi-dimensional risk assessment."),
    ("human", """Assess risk from multiple angles:

Document Analysis: {analysis_text}
Risk Factors: {risk_factors}

Evaluate:
1. Identity risk (0-1)
2. Documentation risk (0-1)
3. Behavioral risk (0-1)
4. Compliance risk (0-1)
5. Overall risk (0-1)

Return JSON with scores and explanation for each dimension.""")
])

# ═════════════════════════════════════════════════════════════
# INTELLIGENCE FUNCTIONS
# ═════════════════════════════════════════════════════════════

def extract_keywords_with_intelligence(text: str) -> Dict[str, Any]:
    """
    Extract meaningful keywords and entities from document
    Provides intelligence metrics for document quality assessment
    """
    # Categorized keywords for better analysis
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
        found = []
        for keyword in keywords:
            if keyword in text_lower:
                found.append(keyword)
        analysis[category] = {
            "keywords": found,
            "count": len(found),
            "coverage": len(found) / len(keywords)
        }
        total_found += len(found)
    
    return {
        "by_category": analysis,
        "total_keywords_found": total_found,
        "keyword_richness": total_found / len(sum(all_keywords.values(), [])),
        "has_identity_info": bool(analysis["identity"]["count"] > 0),
        "has_risk_indicators": bool(analysis["risk"]["count"] > 0),
        "has_financial_info": bool(analysis["financial"]["count"] > 0)
    }

def calculate_document_quality_metrics(text: str, confidence: float, keyword_analysis: Dict) -> Dict[str, float]:
    """
    Calculate comprehensive document quality metrics using multiple factors
    """
    metrics = {}
    
    # 1. Length metrics
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
    
    # 2. Information completeness
    completeness = 0.0
    if keyword_analysis["has_identity_info"]:
        completeness += 0.3
    if keyword_analysis["has_risk_indicators"]:
        completeness += 0.3
    if keyword_analysis["has_financial_info"]:
        completeness += 0.4
    metrics["completeness_score"] = completeness
    
    # 3. Keyword richness
    metrics["keyword_richness_score"] = min(keyword_analysis["keyword_richness"], 1.0)
    
    # 4. Verification confidence
    metrics["verification_confidence"] = confidence
    
    # 5. Overall quality (weighted average)
    weights = {
        "length_score": 0.20,
        "completeness_score": 0.30,
        "keyword_richness_score": 0.25,
        "verification_confidence": 0.25
    }
    
    overall_quality = sum(
        metrics[key] * weights[key] for key in weights.keys()
    )
    metrics["overall_quality_score"] = round(overall_quality, 3)
    
    return metrics

def detect_anomalies(text: str) -> Dict[str, List[str]]:
    """
    Detect anomalies and suspicious patterns in document
    """
    anomalies = {
        "missing_fields": [],
        "suspicious_patterns": [],
        "formatting_issues": [],
        "data_quality_issues": []
    }
    
    text_lower = text.lower()
    
    # Check for missing required fields
    required_fields = ["name", "date", "address"]
    for field in required_fields:
        if field not in text_lower:
            anomalies["missing_fields"].append(field)
    
    # Check for suspicious patterns
    suspicious_patterns = ["unknown", "n/a", "unknown", "not provided", ""]
    for pattern in suspicious_patterns:
        if pattern in text_lower:
            anomalies["suspicious_patterns"].append(f"'{pattern}' found in document")
    
    # Check for formatting inconsistencies
    lines = text.split("\n")
    if len(lines) < 3:
        anomalies["formatting_issues"].append("Very short document")
    
    return anomalies

async def perform_multi_step_langchain_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform sophisticated multi-step analysis using LangChain chains
    
    Steps:
    1. Initial comprehensive analysis
    2. Risk factor extraction
    3. Confidence/completeness assessment
    4. Multi-angle risk scoring
    5. Intelligence aggregation
    """
    
    text = data.get("text", "No text provided")
    verified = data.get("verified", False)
    confidence = data.get("confidence_score", 0.5)
    
    logger.info("═════════════════════════════════════════════════════════")
    logger.info("Starting Advanced LangChain Multi-Step Analysis")
    logger.info("═════════════════════════════════════════════════════════")
    
    try:
        if not llm:
            return {
                "status": "error",
                "error": "LangChain LLM not initialized"
            }
        
        # Intelligence preprocessing
        logger.info("Step 0: Intelligent preprocessing...")
        keyword_analysis = extract_keywords_with_intelligence(text)
        quality_metrics = calculate_document_quality_metrics(text, confidence, keyword_analysis)
        anomalies = detect_anomalies(text)
        logger.info(f"  Quality Score: {quality_metrics['overall_quality_score']}")
        logger.info(f"  Keywords Found: {keyword_analysis['total_keywords_found']}")
        logger.info(f"  Anomalies Detected: {sum(len(v) for v in anomalies.values())}")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 1: INITIAL COMPREHENSIVE ANALYSIS WITH LANGCHAIN
        # ═════════════════════════════════════════════════════════════
        logger.info("Step 1: Performing comprehensive document analysis...")
        
        analysis_chain = analysis_prompt | llm | JsonOutputParser()
        
        initial_analysis = analysis_chain.invoke({
            "document_text": text[:2000],
            "verification_status": "PASSED" if verified else "FAILED",
            "confidence_score": f"{confidence:.2f}"
        })
        
        logger.info("  ✓ Initial analysis completed")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 2: RISK FACTOR EXTRACTION
        # ═════════════════════════════════════════════════════════════
        logger.info("Step 2: Extracting and categorizing risk factors...")
        
        risk_chain = risk_factors_prompt | llm | JsonOutputParser()
        
        analysis_text = json.dumps(initial_analysis, indent=2)
        risk_factors = risk_chain.invoke({
            "analysis_text": analysis_text
        })
        
        logger.info(f"  ✓ Risk factors extracted: {risk_factors.get('risk_factor_count', 0)} factors found")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 3: CONFIDENCE AND COMPLETENESS ASSESSMENT
        # ═════════════════════════════════════════════════════════════
        logger.info("Step 3: Assessing analysis confidence and data quality...")
        
        confidence_chain = confidence_prompt | llm | JsonOutputParser()
        
        confidence_assessment = confidence_chain.invoke({
            "document_text": text[:1000],
            "analysis_text": analysis_text
        })
        
        logger.info(f"  ✓ Confidence: {confidence_assessment.get('overall_confidence', 0):.2f}")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 4: MULTI-ANGLE RISK SCORING
        # ═════════════════════════════════════════════════════════════
        logger.info("Step 4: Performing multi-dimensional risk assessment...")
        
        multi_angle_chain = multi_angle_prompt | llm | JsonOutputParser()
        
        multi_angle_scores = multi_angle_chain.invoke({
            "analysis_text": analysis_text,
            "risk_factors": json.dumps(risk_factors, indent=2)
        })
        
        logger.info("  ✓ Multi-angle scoring completed")
        
        # ═════════════════════════════════════════════════════════════
        # STEP 5: INTELLIGENCE AGGREGATION
        # ═════════════════════════════════════════════════════════════
        logger.info("Step 5: Aggregating intelligence metrics...")
        
        enhanced_analysis = {
            "status": "success",
            "analysis": initial_analysis.get("summary", "KYC Analysis Complete"),
            "model": LLM_MODEL,
            "langchain_enabled": True,
            
            # Primary analysis results
            "kyc_analysis": initial_analysis,
            
            # Risk assessment
            "risk_assessment": {
                "risk_level": initial_analysis.get("risk_level", "medium"),
                "factors": risk_factors,
                "multi_angle_scores": multi_angle_scores,
                "anomalies_detected": anomalies
            },
            
            # Intelligence metrics
            "intelligence_metrics": {
                "document_quality": quality_metrics,
                "keyword_analysis": keyword_analysis,
                "confidence_assessment": confidence_assessment,
                "anomaly_detection": {
                    "total_anomalies": sum(len(v) for v in anomalies.values()),
                    "by_category": anomalies
                }
            },
            
            # Chain execution tracking
            "chain_execution": {
                "steps_completed": [
                    "preprocessing",
                    "initial_analysis",
                    "risk_extraction",
                    "confidence_assessment",
                    "multi_angle_scoring"
                ],
                "total_steps": 5,
                "langchain_chains_used": 4
            },
            
            "timestamp": datetime.now().isoformat()
        }
        
        # Preserve critical KYC document type information from previous agents
        if "document_type" in data:
            enhanced_analysis["document_type"] = data.get("document_type")
        if "confidence" in data:
            enhanced_analysis["confidence"] = data.get("confidence")
        if "is_valid_kyc" in data:
            enhanced_analysis["is_valid_kyc"] = data.get("is_valid_kyc")
        if "all_scores" in data:
            enhanced_analysis["all_scores"] = data.get("all_scores")
        if "reason" in data:
            enhanced_analysis["reason"] = data.get("reason")
        if "filename" in data:
            enhanced_analysis["filename"] = data.get("filename")
        
        # Preserve verification and scoring fields needed by downstream agents
        if "verified" in data:
            enhanced_analysis["verified"] = data.get("verified")
        if "confidence_score" in data:
            enhanced_analysis["confidence_score"] = data.get("confidence_score")
        if "validations" in data:
            enhanced_analysis["validations"] = data.get("validations")
        
        logger.info("═════════════════════════════════════════════════════════")
        logger.info("✓ Advanced LangChain Analysis Complete")
        logger.info("═════════════════════════════════════════════════════════")
        
        return enhanced_analysis
        
    except Exception as e:
        logger.error(f"Error in multi-step analysis: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "fallback": True
        }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reason-agent",
        "version": "2.0.0"
    }

@app.post("/reason")
async def reason(data: Dict[str, Any]):
    """
    Advanced reasoning endpoint with full LangChain intelligence
    
    Features:
    - LangChain prompt templates
    - Multi-step analysis chains
    - Intelligent preprocessing
    - Risk factor extraction
    - Anomaly detection
    - Quality metrics
    - Confidence scoring
    - Multi-dimensional risk assessment
    """
    try:
        logger.info(f"Received reasoning request for analysis")
        
        # Use advanced LangChain analysis
        result = await perform_multi_step_langchain_analysis(data)
        
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
        "agent": "Reason Agent",
        "version": "2.0.0",
        "langchain_enabled": True,
        "features": [
            "LangChain ChatOllama integration",
            "Prompt templates for consistency",
            "Multi-step analysis chains",
            "Intelligent keyword extraction",
            "Document quality metrics",
            "Anomaly detection",
            "Risk factor categorization",
            "Multi-dimensional risk scoring",
            "Confidence assessment",
            "Comprehensive intelligence aggregation"
        ],
        "analysis_steps": 5,
        "models_supported": [LLM_MODEL],
        "context_window": 2048
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

