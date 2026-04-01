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
        
        # Extract intelligence from data
        factors = data.get("intelligence_metrics", {})
        
        analysis = {
            "risk_metrics": {
                "score": risk_score,
                "level": risk_level,
                "verified": verified
            },
            "risk_indicators": self.extract_risk_indicators(data),
            "mitigating_factors": self.extract_mitigating_factors(data),
            "regulatory_concerns": self.extract_regulatory_concerns(data),
            "overall_risk_assessment": self.assess_overall_risk(risk_score, verified)
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
    
    def assess_overall_risk(self, risk_score: float, verified: bool) -> str:
        """Provide overall risk assessment"""
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

        REASONING-DRIVEN: Considers conflict analysis from Reason Agent
        """
        
        # Get confidence score with fallback for field name variations
        confidence_score = data.get("confidence_score", 0.0)
        if confidence_score == 0.0:
            confidence_score = data.get("confidence", 0.0)
        # Extract is_valid_kyc flag from data
        # Check multiple possible sources/formats
        is_valid_kyc = data.get("is_valid_kyc", False)
        document_type = data.get("document_type", "Unknown")
        document_confidence = data.get("confidence", 0.0)

        # ═════════════════════════════════════════════════════════════
        # NEW: Check conflict analysis from Reason Agent
        # ═════════════════════════════════════════════════════════════
        conflict_analysis = data.get("conflict_analysis")
        conflicts_detected = data.get("conflicts_detected", False)
        reasoning_applied = data.get("analysis_pipeline", {}).get("reasoning_applied", False)

        if conflicts_detected and conflict_analysis:
            logger.info(f"\n🧠 REASONING-DRIVEN DECISION MAKING")
            logger.info(f"   Conflicts detected: {conflicts_detected}")
            logger.info(f"   Conflict analysis available: {conflict_analysis is not None}")
            logger.info(f"   Reason Agent recommendation: {conflict_analysis.get('recommendation')}")
            logger.info(f"   Fraud risk assessment: {conflict_analysis.get('fraud_risk')}")
            logger.info(f"   Confidence: {conflict_analysis.get('confidence')}")

            # If Reason Agent found conflicts but low fraud risk, don't auto-reject
            if conflict_analysis.get('fraud_risk') in ['low', 'LOW']:
                logger.info(f"   ✓ Fraud risk is LOW - Not auto-rejecting despite conflicts")
                logger.info(f"   ✓ Using Reason Agent recommendation: {conflict_analysis.get('recommendation')}")

                # Use the Reason Agent's recommendation
                reason_recommendation = conflict_analysis.get('recommendation', 'ESCALATE').upper()
                if reason_recommendation == 'APPROVE':
                    rule = self.DECISION_RULES.get("very_low_risk", self.DECISION_RULES["low_risk"])
                elif reason_recommendation == 'CONDITIONAL':
                    rule = self.DECISION_RULES.get("low_medium_risk", self.DECISION_RULES["medium_risk"])
                else:  # ESCALATE
                    rule = self.DECISION_RULES.get("medium_risk", self.DECISION_RULES["medium_risk"])

                logger.info(f"   ✓ Decision rule applied: {rule['decision']}")
                return self.format_decision(rule, risk_score)

        # Handle string representations of boolean
        if isinstance(is_valid_kyc, str):
            is_valid_kyc = is_valid_kyc.lower() in ('true', '1', 'yes')

        logger.info(f"Decision making - is_valid_kyc: {is_valid_kyc} (type: {type(is_valid_kyc).__name__}), document_type: {document_type}, confidence: {document_confidence}")

        # VALID KYC DOCUMENT TYPES
        valid_kyc_types = ['PAN', 'Aadhar', 'Passport', 'Driving License', 'Voter ID', 'Bank Statement', 'Utility Bill']

        # ═════════════════════════════════════════════════════════════
        # CRITICAL FIX: If document is a valid KYC type with high confidence, APPROVE
        # ═════════════════════════════════════════════════════════════
        if document_type in valid_kyc_types and document_confidence >= 0.99:
            logger.info(f"✅ AUTO-APPROVING: {document_type} with {document_confidence*100:.1f}% confidence")
            rule = {
                "decision": "APPROVED",
                "reason": f"Valid KYC document ({document_type}) identified with {document_confidence*100:.1f}% confidence",
                "confidence_factor": document_confidence,
                "regulatory_action": "APPROVE"
            }
            return self.format_decision(rule, risk_score)

        # CRITICAL: Explicit rejection for Unknown document types
        if document_type == "Unknown" or document_type == "Invalid":
            rule = self.DECISION_RULES["verification_failed"]
            logger.warning(f"🚫 REJECTING: Document type is '{document_type}' - cannot process unknown document types")
            return self.format_decision(rule, risk_score)

        logger.info(f"make_decision - verified: {verified}, confidence_score: {confidence_score:.2%}")

        # Primary check: Verification status WITH confidence override
        # If confidence is high (>=0.8), allow conditional approval even if verification failed on minor check
        if not verified:
            if confidence_score >= 0.8:
                logger.info(f"Verification failed but confidence is high ({confidence_score:.2%}), allowing conditional review")
                rule = self.DECISION_RULES["low_medium_risk"]  # CONDITIONAL_APPROVAL for high confidence
                return self.format_decision(rule, risk_score)
            else:
                logger.warning(f"Verification failed and confidence is low ({confidence_score:.2%}), rejecting")
                rule = self.DECISION_RULES["verification_failed"]
                return self.format_decision(rule, risk_score)
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
        document_type = risk_metrics.get("document_type", "Unknown")

        # Get confidence score with fallback
        confidence_score = risk_metrics.get("confidence_score", 0.0)
        if confidence_score == 0.0:
            confidence_score = risk_metrics.get("confidence", 0.0)

        # CRITICAL: Explicit rejection for Unknown document types
        if document_type == "Unknown" or document_type == "Invalid":
            decision = {
                "decision": "REJECTED",
                "reason": f"Document type is '{document_type}' - cannot process unknown document types",
                "confidence_factor": 1.0,
                "regulatory_action": "REJECT"
            }
        # If document is NOT a valid KYC type AND not verified, reject
        elif not verified and not is_valid_kyc:
            decision = self.DECISION_RULES["verification_failed"]
        # Handle verification with confidence override
        if not verified:
            if confidence_score >= 0.8:
                decision = self.DECISION_RULES["low_medium_risk"]  # CONDITIONAL_APPROVAL for high confidence
            else:
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
        document_type = data.get("document_type", "Unknown")
        document_confidence = data.get("confidence", 0.0)
        
        logger.info(f"Input - risk_score: {risk_score}, risk_level: {risk_level}, verified: {verified}, is_valid_kyc: {is_valid_kyc}, document_type: {document_type}, confidence: {document_confidence}")
        # Handle both "confidence" and "confidence_score" field names
        confidence_score = data.get("confidence_score", 0.0)
        if confidence_score == 0.0:
            # Fallback: check if "confidence" field exists
            confidence_score = data.get("confidence", 0.0)
        logger.info(f"Input - risk_score: {risk_score}, risk_level: {risk_level}, verified: {verified}, confidence_score: {confidence_score:.2%}")

        # VALID KYC DOCUMENT TYPES (from extract-agent)
        valid_kyc_types = ['PAN', 'Aadhar', 'Passport', 'Driving License', 'Voter ID', 'Bank Statement', 'Utility Bill']

        # ═════════════════════════════════════════════════════════════
        # CRITICAL LOGIC: Handle document identification
        # ═════════════════════════════════════════════════════════════

        # Case 1: Document is identified as a VALID KYC type with high confidence (100%)
        # APPROVE immediately - do not reject
        if document_type in valid_kyc_types and document_confidence >= 0.99:
            logger.info(f"✅ APPROVING: Document identified as '{document_type}' with {document_confidence*100:.1f}% confidence")
            approval_result = {
                "status": "success",
                "decision": "APPROVED",
                "reason": f"Valid KYC document identified as {document_type} with {document_confidence*100:.1f}% confidence. Document meets KYC requirements.",

                "confidence_scores": {
                    "decision_confidence": document_confidence,
                    "document_identification_confidence": document_confidence,
                    "risk_adjusted_confidence": max(0.0, document_confidence - (risk_score * 0.1))
                },

                "confidence": document_confidence,
                "document_confidence": document_confidence,

                "regulatory_action": "APPROVE",
                "requires_human_review": False,

                "risk_score": risk_score,
                "risk_level": risk_level,
                "document_type": document_type,
                "is_valid_kyc": True,

                "analysis": {
                    "risk_factors_summary": [],
                    "mitigating_factors": [f"✓ Valid {document_type} identified with {document_confidence*100:.1f}% confidence"],
                    "regulatory_concerns": [],
                    "overall_assessment": f"APPROVAL - {document_type} is a valid KYC document with high confidence identification"
                },

                "input_metrics": {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "verified": verified,
                    "extraction_confidence_score": data.get("confidence_score", 0.0),
                    "document_identification_confidence": document_confidence
                }
            }
            return approval_result

        # Case 2: Document type is truly Unknown or Invalid - REJECT
        # CRITICAL FIX: Explicit rejection for Unknown document types
        if document_type == "Unknown" or document_type == "Invalid":
            logger.warning(f"🚫 CRITICAL: Document identified as '{document_type}' - MUST BE REJECTED")
            rejection_result = {
                "status": "success",
                "decision": "REJECTED",
                "reason": f"Document type is '{document_type}' - cannot process unknown or invalid documents. Please submit a valid KYC document (PAN, Aadhar, Passport, Driving License, Voter ID, Bank Statement, or Utility Bill).",

                "confidence_scores": {
                    "decision_confidence": 1.0,
                    "document_identification_confidence": document_confidence,
                    "risk_adjusted_confidence": 1.0
                },

                "confidence": 1.0,
                "document_confidence": document_confidence,

                "regulatory_action": "REJECT",
                "requires_human_review": False,

                "risk_score": risk_score,
                "risk_level": risk_level,
                "document_type": document_type,
                "is_valid_kyc": False,

                "analysis": {
                    "risk_factors_summary": ["Unknown/Invalid document type - cannot verify"],
                    "mitigating_factors": [],
                    "regulatory_concerns": ["Document type not recognized - rejected for compliance"],
                    "overall_assessment": f"REJECTION - Document type '{document_type}' is not a supported KYC document"
                },

                "input_metrics": {
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "verified": verified,
                    "extraction_confidence_score": data.get("confidence_score", 0.0),
                    "document_identification_confidence": document_confidence
                },

                "decision_version": "2.0.0 (Advanced)",
                "timestamp": datetime.now().isoformat()
            }

            logger.error(f"✗ DECISION: REJECTED | Document: {document_type} | Confidence: 100%")
            return rejection_result

        # If document is a valid type (e.g., Aadhar, PAN, etc.) but confidence is low (30-50%)
        # AND is_valid_kyc is True, we should proceed but note the low confidence
        if is_valid_kyc and document_confidence < 0.5:
            logger.warning(f"⚠️  CAUTION: Valid KYC document type '{document_type}' but with lower confidence ({document_confidence:.1%}). Will proceed with enhanced scrutiny.")
            # Add extra risk adjustment for low confidence
            risk_score = min(risk_score + 0.1, 1.0)  # Increase risk slightly for low confidence
            logger.info(f"Risk score adjusted to {risk_score} due to low document confidence")

        # Log all data keys for debugging
        logger.info(f"All input data keys: {list(data.keys())}")
        if not verified:
            logger.warning(f"⚠️  WARNING: verified field is False - confidence_score is {confidence_score:.2%}")
            if confidence_score >= 0.8:
                logger.info("✓ Confidence override will be applied (confidence >= 80%)")
        
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
        
        # Extract document identification confidence from extract agent
        document_identification_confidence = data.get("confidence", 0.0)

        # Build comprehensive result
        result = {
            "status": "success",
            "decision": decision_result["decision"],
            "reason": decision_result["reason"],

            # CLARITY: Separate decision confidence from document confidence
            "confidence_scores": {
                "decision_confidence": round(decision_result["confidence"], 3),
                "document_identification_confidence": round(document_identification_confidence, 3),
                "risk_adjusted_confidence": round(decision_result["risk_adjusted_confidence"], 3)
            },

            # For backward compatibility, include main confidence
            "confidence": round(decision_result["confidence"], 3),
            "document_confidence": round(document_identification_confidence, 3),

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
                "extraction_confidence_score": data.get("confidence_score", 0.0),
                "document_identification_confidence": document_identification_confidence
            },
            
            "decision_version": "2.0.0 (Advanced)",
            "timestamp": datetime.now().isoformat()
        }
        
        # Preserve critical KYC document type information from previous agents
        if "document_type" in data:
            result["document_type"] = data.get("document_type")
        if "is_valid_kyc" in data:
            result["is_valid_kyc"] = data.get("is_valid_kyc")
            logger.info(f"Document is valid KYC: {result['is_valid_kyc']}")
        if "all_scores" in data:
            result["all_scores"] = data.get("all_scores")
        if "reason" in data:
            result["reason_from_extract"] = data.get("reason")
        if "filename" in data:
            result["filename"] = data.get("filename")
        
        logger.info(f"✓ Decision: {result['decision']} | Confidence: {result['confidence']:.1%}")
        logger.info(f"Document Identification Confidence: {document_identification_confidence:.1%}")
        logger.info(f"Document Type: {result.get('document_type', 'Unknown')}")
        logger.info(f"Is Valid KYC: {result.get('is_valid_kyc', False)}")
        logger.info(f"Risk Score: {risk_score}")
        logger.info(f"Verified: {verified}")
        logger.info(f"Confidence Breakdown: Decision={result['confidence']:.1%}, DocID={document_identification_confidence:.1%}, RiskAdj={result['confidence_scores']['risk_adjusted_confidence']:.1%}")
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
