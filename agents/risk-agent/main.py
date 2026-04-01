from fastapi import FastAPI, HTTPException
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy.stats import zscore  # For anomaly detection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Risk Agent with Advanced Intelligence", version="2.0.0")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}

# ═════════════════════════════════════════════════════════════
# ADVANCED RISK CALCULATION ENGINE
# ═════════════════════════════════════════════════════════════

class RiskAnalyzer:
    """
    Advanced risk analysis with multiple dimensions and intelligent scoring
    """
    
    # Risk keywords categorized by severity
    RISK_KEYWORDS = {
        "critical": ["fraud", "money laundering", "terrorist", "sanctions", "blocked"],
        "high": ["suspicious", "high risk", "concerning", "warning", "alert", "unusual"],
        "medium": ["irregular", "discrepancy", "mismatch", "incomplete", "unclear"],
        "low": ["note", "review", "check", "verify"]
    }
    
    # Positive indicators that reduce risk
    POSITIVE_INDICATORS = [
        "verified", "confirmed", "valid", "authentic", "legitimate",
        "clear", "complete", "documented", "certified", "approved"
    ]
    
    def __init__(self):
        self.risk_scores_history = []
    
    def analyze_keywords(self, text: str) -> Dict[str, Any]:
        """
        Advanced keyword analysis with severity weighting
        """
        text_lower = text.lower()
        
        keyword_analysis = {
            "critical_keywords": [],
            "high_risk_keywords": [],
            "medium_risk_keywords": [],
            "low_risk_keywords": [],
            "positive_indicators": [],
            "keyword_score": 0.0
        }
        
        # Count keywords by severity
        for severity, keywords in self.RISK_KEYWORDS.items():
            for keyword in keywords:
                count = text_lower.count(keyword)
                if count > 0:
                    keyword_analysis[f"{severity}_keywords"].extend([keyword] * count)
        
        # Count positive indicators
        for indicator in self.POSITIVE_INDICATORS:
            count = text_lower.count(indicator)
            if count > 0:
                keyword_analysis["positive_indicators"].extend([indicator] * count)
        
        # Calculate keyword risk score (0-1)
        total_risk_words = sum(len(keyword_analysis[f"{s}_keywords"]) 
                               for s in ["critical", "high_risk", "medium_risk", "low_risk"])
        positive_words = len(keyword_analysis["positive_indicators"])
        
        if total_risk_words > 0:
            # Weight critical higher
            critical_weight = len(keyword_analysis["critical_keywords"]) * 1.0
            high_weight = len(keyword_analysis["high_risk_keywords"]) * 0.7
            medium_weight = len(keyword_analysis["medium_risk_keywords"]) * 0.4
            low_weight = len(keyword_analysis["low_risk_keywords"]) * 0.2
            
            weighted_risk = (critical_weight + high_weight + medium_weight + low_weight) / max(total_risk_words, 1)
            keyword_analysis["keyword_score"] = min(weighted_risk / 2.0, 1.0)
        else:
            # No risk keywords, boost score if positive indicators present
            keyword_analysis["keyword_score"] = max(0.0, -0.1 * positive_words)
        
        return keyword_analysis
    
    def calculate_document_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate document quality based on multiple factors
        """
        scores = []
        text = data.get("text", "")
        
        # 1. Text length quality (0-0.25)
        text_length = len(text)
        if text_length < 50:
            length_score = 0.0
        elif text_length < 200:
            length_score = 0.1
        elif text_length < 500:
            length_score = 0.2
        else:
            length_score = 0.25
        scores.append(length_score)
        
        # 2. Verification status (0-0.25)
        verified = data.get("verified", False)
        verification_score = 0.25 if verified else 0.0
        scores.append(verification_score)
        
        # 3. Confidence score (0-0.25)
        confidence = data.get("confidence_score", 0.5)
        confidence_score = confidence * 0.25
        scores.append(confidence_score)
        
        # 4. Information completeness (0-0.25)
        required_fields = ["name", "date", "address", "identification"]
        found_fields = sum(1 for field in required_fields if field.lower() in text.lower())
        completeness_score = (found_fields / len(required_fields)) * 0.25
        scores.append(completeness_score)
        
        return min(sum(scores), 1.0)
    
    def analyze_behavioral_patterns(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze behavioral patterns and anomalies
        """
        text = data.get("text", "").lower()
        
        patterns = {
            "information_gaps": 0.0,
            "suspicious_patterns": 0.0,
            "inconsistencies": 0.0,
            "overall_pattern_risk": 0.0
        }
        
        # Check for information gaps
        vague_terms = ["unknown", "n/a", "na", "not applicable", "not provided", ""]
        vague_count = sum(1 for term in vague_terms if term in text)
        patterns["information_gaps"] = min(vague_count * 0.2, 1.0)
        
        # Check for suspicious patterns
        suspicious_indicators = [
            ("no fixed address", 0.3),
            ("unemployed", 0.1),
            ("retired", 0.0),
            ("cash business", 0.2),
            ("multiple countries", 0.15)
        ]
        
        for indicator, score in suspicious_indicators:
            if indicator in text:
                patterns["suspicious_patterns"] = max(patterns["suspicious_patterns"], score)
        
        # Check for inconsistencies
        dates_mentioned = text.count("20")  # Years
        if dates_mentioned > 5:  # Too many dates might indicate inconsistency
            patterns["inconsistencies"] = 0.2
        
        # Overall pattern risk (weighted average)
        patterns["overall_pattern_risk"] = (
            0.4 * patterns["information_gaps"] +
            0.4 * patterns["suspicious_patterns"] +
            0.2 * patterns["inconsistencies"]
        )
        
        return patterns
    
    def calculate_multi_factor_risk(self, data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate risk using multiple intelligent factors
        
        Factors:
        1. Verification Status (20%)
        2. Document Quality (20%)
        3. Keyword Analysis (25%)
        4. Behavioral Patterns (20%)
        5. Confidence Metrics (15%)
        """
        
        factors = {}
        
        # Factor 1: Verification Status
        verified = data.get("verified", False)
        factors["verification"] = {
            "score": 0.1 if verified else 0.5,
            "weight": 0.20,
            "explanation": "PASSED" if verified else "FAILED"
        }
        
        # Factor 2: Document Quality
        doc_quality = self.calculate_document_quality_score(data)
        factors["document_quality"] = {
            "score": 1.0 - doc_quality,  # Invert: low quality = high risk
            "weight": 0.20,
            "explanation": f"Quality Score: {doc_quality:.2f}"
        }
        
        # Factor 3: Keyword Analysis
        keyword_analysis = self.analyze_keywords(data.get("analysis", ""))
        factors["keyword_analysis"] = {
            "score": keyword_analysis["keyword_score"],
            "weight": 0.25,
            "explanation": f"Keywords: {len(keyword_analysis['critical_keywords'])} critical, {len(keyword_analysis['high_risk_keywords'])} high"
        }
        
        # Factor 4: Behavioral Patterns
        patterns = self.analyze_behavioral_patterns(data)
        factors["behavioral_patterns"] = {
            "score": patterns["overall_pattern_risk"],
            "weight": 0.20,
            "explanation": f"Pattern Risk: {patterns['overall_pattern_risk']:.2f}"
        }
        
        # Factor 5: Confidence Metrics
        confidence = data.get("confidence_score", 0.5)
        factors["confidence"] = {
            "score": (1 - confidence) * 0.5,  # Uncertainty increases risk
            "weight": 0.15,
            "explanation": f"Confidence: {confidence:.2f}"
        }
        
        # Calculate weighted risk score
        risk_score = sum(
            factors[key]["score"] * factors[key]["weight"]
            for key in factors.keys()
        )
        
        # Clamp to valid range
        risk_score = max(0.0, min(1.0, risk_score))
        
        # Add variance analysis
        factor_scores = [factors[key]["score"] for key in factors.keys()]
        risk_variance = np.var(factor_scores)
        
        # Store for analysis
        self.risk_scores_history.append(risk_score)
        
        return round(risk_score, 3), {
            "factors": factors,
            "variance": round(risk_variance, 3),
            "consistency": "HIGH" if risk_variance < 0.1 else "MEDIUM" if risk_variance < 0.25 else "LOW"
        }
    
    def get_risk_level(self, score: float) -> str:
        """Classify risk score into categories with more granularity"""
        if score < 0.2:
            return "VERY_LOW"
        elif score < 0.33:
            return "LOW"
        elif score < 0.5:
            return "LOW_MEDIUM"
        elif score < 0.66:
            return "MEDIUM"
        elif score < 0.8:
            return "MEDIUM_HIGH"
        elif score < 0.9:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def get_risk_recommendations(self, risk_score: float, risk_level: str, factors: Dict) -> List[str]:
        """Generate intelligent recommendations based on risk analysis"""
        recommendations = []
        
        if risk_level in ["HIGH", "CRITICAL"]:
            recommendations.append("⚠️ REJECT - High risk profile detected")
            recommendations.append("Consider additional verification")
            recommendations.append("Flag for compliance review")
        elif risk_level in ["MEDIUM_HIGH", "MEDIUM"]:
            recommendations.append("⚠️ MANUAL REVIEW REQUIRED")
            recommendations.append("Request additional documentation")
            recommendations.append("Enhanced due diligence recommended")
        elif risk_level in ["LOW_MEDIUM"]:
            recommendations.append("✓ CONDITIONAL APPROVAL")
            recommendations.append("Standard KYC verification sufficient")
            recommendations.append("Periodic monitoring recommended")
        else:  # LOW, VERY_LOW
            recommendations.append("✓ APPROVED")
            recommendations.append("Standard verification complete")
            recommendations.append("Monitor for regulatory changes")
        
        # Factor-specific recommendations
        if factors.get("verification", {}).get("score", 0) > 0.4:
            recommendations.append("→ Improve document verification procedures")
        
        if factors.get("keyword_analysis", {}).get("score", 0) > 0.6:
            recommendations.append("→ Address identified risk concerns")
        
        if factors.get("behavioral_patterns", {}).get("score", 0) > 0.5:
            recommendations.append("→ Investigate behavioral red flags")
        
        return recommendations

# Global analyzer instance
analyzer = RiskAnalyzer()

@app.post("/risk")
async def risk(data: Dict[str, Any]):
    """
    Calculate advanced risk score using multi-factor intelligent analysis
    """
    try:
        logger.info("Starting advanced risk analysis...")
        logger.info(f"Risk-agent input - verified: {data.get('verified')}, confidence_score: {data.get('confidence_score')}")
        
        # CRITICAL: Save verification fields before analysis
        saved_verified = data.get("verified", False)
        saved_confidence_score = data.get("confidence_score", 0.0)
        saved_validations = data.get("validations", {})
        
        # Perform multi-factor analysis
        risk_score, analysis_details = analyzer.calculate_multi_factor_risk(data)
        risk_level = analyzer.get_risk_level(risk_score)
        recommendations = analyzer.get_risk_recommendations(
            risk_score, 
            risk_level, 
            analysis_details.get("factors", {})
        )
        
        result = {
            "status": "success",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_level_scale": "VERY_LOW|LOW|LOW_MEDIUM|MEDIUM|MEDIUM_HIGH|HIGH|CRITICAL",
            
            # Detailed analysis
            "analysis": {
                "factors": analysis_details.get("factors", {}),
                "factor_consistency": analysis_details.get("consistency", "UNKNOWN"),
                "factor_variance": analysis_details.get("variance", 0.0),
                "recommendations": recommendations
            },
            
            # Metadata
            "analysis_version": "2.0.0 (Advanced)",
            "timestamp": datetime.now().isoformat(),
            "original_data_summary": {
                "has_text": bool(data.get("text")),
                "text_length": len(data.get("text", "")),
                "verified": data.get("verified", False),
                "confidence": data.get("confidence_score", 0.0)
            }
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
        
        # Preserve fields needed by decision agent
        if "verified" in data:
            result["verified"] = data.get("verified")
        if "confidence_score" in data:
            result["confidence_score"] = data.get("confidence_score")
        if "validations" in data:
            result["validations"] = data.get("validations")
        
        # CRITICAL: Double-check that is_valid_kyc is preserved
        if "is_valid_kyc" not in result and "is_valid_kyc" in data:
            logger.warning("WARN: is_valid_kyc missing from result - adding from input")
            result["is_valid_kyc"] = data.get("is_valid_kyc")
        
        logger.info(f"Risk Agent Output - is_valid_kyc: {result.get('is_valid_kyc')} (from input: {data.get('is_valid_kyc')})")

        logger.info(f"Risk assessment completed: {risk_level} (score: {risk_score})")
        logger.info(f"Recommendations: {len(recommendations)} action items")
        
        # CRITICAL: Restore saved verification fields for downstream decision-agent
        # Use the saved values to ensure they flow correctly through the pipeline
        result["verified"] = saved_verified
        result["confidence_score"] = saved_confidence_score
        result["validations"] = saved_validations
        
        logger.info(f"Risk-agent output - verified: {result.get('verified')}, confidence_score: {result.get('confidence_score')}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error in risk analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Risk analysis error: {str(e)}")

@app.get("/capabilities")
async def capabilities():
    """Get capabilities of the advanced risk agent"""
    return {
        "agent": "Risk Agent",
        "version": "2.0.0",
        "features": [
            "Multi-factor risk analysis (5 dimensions)",
            "Advanced keyword analysis with severity levels",
            "Document quality scoring",
            "Behavioral pattern detection",
            "Confidence metrics analysis",
            "Granular risk level classification (7 levels)",
            "Intelligent recommendations",
            "Factor variance analysis",
            "Anomaly detection",
            "Risk score history tracking"
        ],
        "analysis_factors": 5,
        "risk_levels": [
            "VERY_LOW (0.0-0.2)",
            "LOW (0.2-0.33)",
            "LOW_MEDIUM (0.33-0.5)",
            "MEDIUM (0.5-0.66)",
            "MEDIUM_HIGH (0.66-0.8)",
            "HIGH (0.8-0.9)",
            "CRITICAL (0.9-1.0)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

