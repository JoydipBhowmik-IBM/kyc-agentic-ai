from fastapi import FastAPI, HTTPException
import logging
from datetime import datetime
from typing import Dict, Any, List
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LangChain imports for decision-making (optional, for future enhancement)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")

# LLM support is optional
llm = None
try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_URL,
        temperature=0.1,
    )
    logger.info(f"LLM initialized successfully with model: {LLM_MODEL}")
except ImportError:
    logger.info("LangChain not available - LLM features disabled")
except Exception as e:
    logger.warning(f"Failed to initialize LLM: {str(e)}")
    llm = None

# FastAPI app initialization
app = FastAPI(title="Decision Agent", version="2.0.0")

# Decision thresholds
VERY_LOW_RISK_THRESHOLD = 0.2
LOW_RISK_THRESHOLD = 0.33
MEDIUM_LOW_THRESHOLD = 0.5
MEDIUM_RISK_THRESHOLD = 0.66
MEDIUM_HIGH_THRESHOLD = 0.8
HIGH_RISK_THRESHOLD = 0.9

# ═════════════════════════════════════════════════════════════
# DECISION MAKING SYSTEM
# ═════════════════════════════════════════════════════════════

class DecisionEngine:
    """
    Advanced decision-making with explainability and governance
    """
    
    # Decision rules with confidence multipliers
    DECISION_RULES = {
        "verification_failed": {
            "decision": "REJECTED",
            "reason": "Document verification failed - unable to proceed",
            "confidence_factor": 1.0,
            "regulatory_action": "REJECT"
        },
        "critical_risk": {
            "decision": "REJECTED",
            "reason": "Critical risk profile detected - potential fraud or AML concern",
            "confidence_factor": 1.0,
            "regulatory_action": "ESCALATE_AND_REJECT"
        },
        "high_risk": {
            "decision": "REVIEW",
            "reason": "High risk profile requires manual review",
            "confidence_factor": 0.95,
            "regulatory_action": "ESCALATE_FOR_REVIEW"
        },
        "medium_high_risk": {
            "decision": "CONDITIONAL_REVIEW",
            "reason": "Medium-high risk requires enhanced due diligence",
            "confidence_factor": 0.85,
            "regulatory_action": "ENHANCED_VERIFICATION"
        },
        "medium_risk": {
            "decision": "REVIEW",
            "reason": "Medium risk - standard enhanced due diligence needed",
            "confidence_factor": 0.75,
            "regulatory_action": "STANDARD_REVIEW"
        },
        "low_medium_risk": {
            "decision": "CONDITIONAL_APPROVAL",
            "reason": "Low-medium risk - may proceed with standard controls",
            "confidence_factor": 0.80,
            "regulatory_action": "STANDARD_APPROVAL"
        },
        "low_risk": {
            "decision": "APPROVED",
            "reason": "Low risk profile - standard KYC verification sufficient",
            "confidence_factor": 0.85,
            "regulatory_action": "APPROVE"
        },
        "very_low_risk": {
            "decision": "APPROVED",
            "reason": "Very low risk profile - minimal concerns detected",
            "confidence_factor": 0.90,
            "regulatory_action": "APPROVE"
        }
    }
    
    def __init__(self):
        self.decision_history = []
        self.decision_count = 0
    
    def analyze_risk_factors(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze all risk factors for comprehensive decision making
        """
        risk_score = data.get("risk_score", 0.5)
        risk_level = data.get("risk_level", "MEDIUM")
        verified = data.get("verified", False)
        is_valid_kyc = data.get("is_valid_kyc", False)
        
        # Extract intelligence from data
        factors = data.get("intelligence_metrics", {})
        
        analysis = {
            "risk_metrics": {
                "score": risk_score,
                "level": risk_level,
                "verified": verified,
                "is_valid_kyc": is_valid_kyc
            },
            "risk_indicators": self.extract_risk_indicators(data),
            "mitigating_factors": self.extract_mitigating_factors(data),
            "regulatory_concerns": self.extract_regulatory_concerns(data),
            "overall_risk_assessment": self.assess_overall_risk(risk_score, verified, is_valid_kyc)
        }
        
        return analysis
    
    def extract_risk_indicators(self, data: Dict[str, Any]) -> List[str]:
        """Extract specific risk indicators from data"""
        indicators = []
        risk_level = data.get("risk_level", "").upper()
        
        # Map risk level to indicators
        risk_maps = {
            "CRITICAL": ["Potential fraud", "Money laundering suspicion", "Sanctions concerns"],
            "HIGH": ["Multiple red flags", "Suspicious patterns", "Inconsistent information"],
            "MEDIUM_HIGH": ["Some concerns identified", "Requires closer inspection"],
            "MEDIUM": ["Standard AML checks needed", "Documentation issues"],
            "LOW_MEDIUM": ["Minor documentation gaps"],
            "LOW": [],
            "VERY_LOW": []
        }
        
        return risk_maps.get(risk_level, [])
    
    def extract_mitigating_factors(self, data: Dict[str, Any]) -> List[str]:
        """Extract factors that reduce risk"""
        factors = []
        
        if data.get("verified", False):
            factors.append("✓ Document verification passed")
        
        if data.get("is_valid_kyc", False):
            factors.append("✓ Valid KYC document type identified")
        
        if data.get("confidence", 0) >= 0.9:
            factors.append("✓ High document identification confidence")
        
        if data.get("confidence_score", 0) > 0.8:
            factors.append("✓ High extraction confidence")
        
        if "analysis" in data and len(str(data["analysis"])) > 100:
            factors.append("✓ Comprehensive document content")
        
        return factors
    
    def extract_regulatory_concerns(self, data: Dict[str, Any]) -> List[str]:
        """Extract regulatory compliance concerns"""
        concerns = []
        risk_score = data.get("risk_score", 0.5)
        
        if risk_score > 0.8:
            concerns.append("HIGH: Potential AML/CFT red flags")
        elif risk_score > 0.66:
            concerns.append("MEDIUM: Enhanced due diligence required")
        elif risk_score > 0.5:
            concerns.append("MEDIUM: Standard verification procedures")
        
        return concerns
    
    def assess_overall_risk(self, risk_score: float, verified: bool, is_valid_kyc: bool = False) -> str:
        """Provide overall risk assessment"""
        # If it's a valid KYC document that passed verification, risk is reduced
        if is_valid_kyc and verified:
            if risk_score < 0.2:
                return "MINIMAL RISK - Valid KYC document with low regulatory concern"
            elif risk_score < 0.33:
                return "LOW RISK - Valid KYC document, standard controls sufficient"
            elif risk_score < 0.5:
                return "LOW-MEDIUM RISK - Valid KYC document, enhanced controls recommended"
        
        if not verified:
            return "UNVERIFIED - Cannot proceed"
        elif risk_score < 0.2:
            return "MINIMAL RISK - Low regulatory concern"
        elif risk_score < 0.33:
            return "LOW RISK - Standard controls sufficient"
        elif risk_score < 0.5:
            return "LOW-MEDIUM RISK - Enhanced controls recommended"
        elif risk_score < 0.66:
            return "MEDIUM RISK - Manual review required"
        elif risk_score < 0.8:
            return "MEDIUM-HIGH RISK - Enhanced scrutiny needed"
        else:
            return "HIGH/CRITICAL RISK - Escalation recommended"
    
    def make_decision(self, risk_score: float, risk_level: str, verified: bool, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make final KYC decision based on comprehensive analysis
        """
        
        # Extract is_valid_kyc flag from data
        # Check multiple possible sources/formats
        is_valid_kyc = data.get("is_valid_kyc", False)
        
        # Handle string representations of boolean
        if isinstance(is_valid_kyc, str):
            is_valid_kyc = is_valid_kyc.lower() in ('true', '1', 'yes')
        
        logger.info(f"Decision making - is_valid_kyc: {is_valid_kyc} (type: {type(is_valid_kyc).__name__})")
        
        # Primary check: If document is NOT a valid KYC type AND not verified, reject
        # But if it IS a valid KYC document type, we proceed with risk-based decision
        # IMPORTANT: If is_valid_kyc=True, the document passed KYC classification, so we proceed based on risk
        if not verified and not is_valid_kyc:
            rule = self.DECISION_RULES["verification_failed"]
            logger.warning(f"Rejecting: not verified ({verified}) and not valid KYC ({is_valid_kyc})")
            return self.format_decision(rule, risk_score)
        elif not verified and is_valid_kyc:
            logger.info(f"Proceeding with risk-based decision: verified={verified}, is_valid_kyc={is_valid_kyc}, risk_level={risk_level}")
        
        # Map risk level to decision rule
        rule_key = risk_level.lower() if risk_level else "medium_risk"
        
        # Handle unmapped risk levels
        risk_mapping = {
            "very_low": "very_low_risk",
            "low": "low_risk",
            "low_medium": "low_medium_risk",
            "medium": "medium_risk",
            "medium_high": "medium_high_risk",
            "high": "high_risk",
            "critical": "critical_risk"
        }
        
        rule_key = risk_mapping.get(risk_level.lower(), "medium_risk")
        
        if rule_key not in self.DECISION_RULES:
            rule_key = "medium_risk"
        
        rule = self.DECISION_RULES[rule_key]
        return self.format_decision(rule, risk_score)
    
    def format_decision(self, rule: Dict[str, Any], risk_score: float) -> Dict[str, Any]:
        """Format decision with all metadata"""
        return {
            "decision": rule["decision"],
            "reason": rule["reason"],
            "confidence": rule["confidence_factor"],
            "risk_adjusted_confidence": max(0.0, rule["confidence_factor"] - (risk_score * 0.1)),
            "regulatory_action": rule["regulatory_action"],
            "requires_human_review": rule["decision"] in ["REVIEW", "CONDITIONAL_REVIEW", "CONDITIONAL_APPROVAL"]
        }
    
    def generate_decision_explanation(self, data: Dict[str, Any], decision_result: Dict[str, Any]) -> str:
        """Generate human-readable explanation of decision"""
        lines = [
            f"Decision: {decision_result['decision']}",
            f"Reason: {decision_result['reason']}",
            f"Confidence: {decision_result['confidence']:.2%}",
            f"Regulatory Action: {decision_result['regulatory_action']}"
        ]
        
        if decision_result["requires_human_review"]:
            lines.append("⚠️ Human Review Required")
        
        return "\n".join(lines)
    
    def explain_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an explainable decision based on analysis."""
        risk_metrics = analysis.get("risk_metrics", {})
        risk_score = risk_metrics.get("score", 0.5)
        verified = risk_metrics.get("verified", False)
        is_valid_kyc = risk_metrics.get("is_valid_kyc", False)

        # If document is NOT a valid KYC type AND not verified, reject
        # But if it IS valid KYC, use risk-based decision
        if not verified and not is_valid_kyc:
            decision = self.DECISION_RULES["verification_failed"]
        elif risk_score >= HIGH_RISK_THRESHOLD:
            decision = self.DECISION_RULES["critical_risk"]
        elif risk_score >= MEDIUM_HIGH_THRESHOLD:
            decision = self.DECISION_RULES["high_risk"]
        elif risk_score >= MEDIUM_RISK_THRESHOLD:
            decision = self.DECISION_RULES["medium_risk"]
        elif risk_score >= LOW_RISK_THRESHOLD:
            decision = self.DECISION_RULES["low_risk"]
        else:
            decision = self.DECISION_RULES["very_low_risk"]

        explanation = {
            "decision": decision["decision"],
            "reason": decision["reason"],
            "confidence_factor": decision["confidence_factor"],
            "regulatory_action": decision["regulatory_action"],
            "risk_analysis": analysis
        }

        return explanation

# Global decision engine
decision_engine = DecisionEngine()

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "version": "2.0.0"}

@app.post("/decision")
async def decision(data: Dict[str, Any]):
    """
    Make final KYC decision with comprehensive analysis
    """
    try:
        logger.info("Making final KYC decision with advanced analysis...")
        logger.info(f"Received data keys: {list(data.keys())}")
        
        # Extract decision inputs
        risk_score = data.get("risk_score", 0.5)
        risk_level = data.get("risk_level", "MEDIUM")
        verified = data.get("verified", False)
        is_valid_kyc = data.get("is_valid_kyc", False)
        
        logger.info(f"Input - risk_score: {risk_score}, risk_level: {risk_level}, verified: {verified}, is_valid_kyc: {is_valid_kyc}")
        
        # Log all data keys for debugging
        logger.info(f"All input data keys: {list(data.keys())}")
        
        # IMPORTANT: If extract agent identified this as a valid KYC document but verify agent couldn't verify,
        # we should still allow it to proceed with caution (not auto-reject)
        if not verified and is_valid_kyc:
            logger.info("Document is valid KYC type but verification incomplete - will be reviewed based on risk score")
        
        if not verified and not is_valid_kyc:
            logger.warning("⚠️  WARNING: Document failed KYC validation - will be rejected")
        
        # Perform comprehensive risk analysis
        risk_analysis = decision_engine.analyze_risk_factors(data)
        
        # Make decision
        decision_result = decision_engine.make_decision(
            risk_score, 
            risk_level, 
            verified,
            data
        )
        
        # Generate explanation
        explanation = decision_engine.generate_decision_explanation(data, decision_result)
        
        # Build comprehensive result
        result = {
            "status": "success",
            "decision": decision_result["decision"],
            "reason": decision_result["reason"],
            "confidence": round(decision_result["confidence"], 3),
            "risk_adjusted_confidence": round(decision_result["risk_adjusted_confidence"], 3),
            "regulatory_action": decision_result["regulatory_action"],
            "requires_human_review": decision_result["requires_human_review"],
            
            # Include risk metrics for frontend display
            "risk_score": risk_score,
            "risk_level": risk_level,
            
            # Detailed analysis
            "analysis": {
                "risk_factors_summary": risk_analysis["risk_indicators"],
                "mitigating_factors": risk_analysis["mitigating_factors"],
                "regulatory_concerns": risk_analysis["regulatory_concerns"],
                "overall_assessment": risk_analysis["overall_risk_assessment"],
                "explanation": explanation
            },
            
            # Decision metadata
            "input_metrics": {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "verified": verified,
                "confidence_score": data.get("confidence_score", 0.0)
            },
            
            "decision_version": "2.0.0 (Advanced)",
            "timestamp": datetime.now().isoformat()
        }
        
        # Preserve critical KYC document type information from previous agents
        if "document_type" in data:
            result["document_type"] = data.get("document_type")
        if "confidence" in data:
            result["confidence"] = data.get("confidence")
        if "is_valid_kyc" in data:
            result["is_valid_kyc"] = data.get("is_valid_kyc")
        if "all_scores" in data:
            result["all_scores"] = data.get("all_scores")
        if "reason" in data:
            result["reason"] = data.get("reason")
        if "filename" in data:
            result["filename"] = data.get("filename")
        
        logger.info(f"✓ Decision: {result['decision']} | Confidence: {result['confidence']:.1%}")
        logger.info(f"Final result keys being returned: {list(result.keys())}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error in decision: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Decision error: {str(e)}")

@app.get("/decision-rules")
async def get_decision_rules():
    """Get all decision rules for transparency"""
    return {
        "version": "2.0.0",
        "decision_framework": "Multi-factor risk-based",
        "rules": decision_engine.DECISION_RULES,
        "thresholds": {
            "very_low_risk": f"0.0 - {VERY_LOW_RISK_THRESHOLD}",
            "low_risk": f"{VERY_LOW_RISK_THRESHOLD} - {LOW_RISK_THRESHOLD}",
            "low_medium_risk": f"{LOW_RISK_THRESHOLD} - {MEDIUM_LOW_THRESHOLD}",
            "medium_risk": f"{MEDIUM_LOW_THRESHOLD} - {MEDIUM_RISK_THRESHOLD}",
            "medium_high_risk": f"{MEDIUM_RISK_THRESHOLD} - {MEDIUM_HIGH_THRESHOLD}",
            "high_risk": f"{MEDIUM_HIGH_THRESHOLD} - {HIGH_RISK_THRESHOLD}",
            "critical_risk": f"{HIGH_RISK_THRESHOLD} - 1.0"
        }
    }

@app.get("/capabilities")
async def capabilities():
    """Get capabilities of the advanced decision agent"""
    return {
        "agent": "Decision Agent",
        "version": "2.0.0",
        "features": [
            "Advanced risk-factor analysis",
            "Explainable decision making",
            "Regulatory compliance framework",
            "Confidence scoring with risk adjustment",
            "Human review escalation logic",
            "Comprehensive risk assessment",
            "Decision rule transparency",
            "Multi-dimensional risk analysis",
            "Mitigating factors evaluation",
            "Regulatory concerns flagging"
        ],
        "decision_types": [
            "APPROVED",
            "CONDITIONAL_APPROVAL",
            "REVIEW",
            "CONDITIONAL_REVIEW",
            "REJECTED"
        ],
        "regulatory_actions": [
            "APPROVE",
            "STANDARD_APPROVAL",
            "ENHANCED_VERIFICATION",
            "STANDARD_REVIEW",
            "ESCALATE_FOR_REVIEW",
            "ESCALATE_AND_REJECT",
            "REJECT"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(app, host="0.0.0.0", port=8000)
