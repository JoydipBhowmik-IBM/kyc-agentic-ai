"""
MCP Server for KYC Agentic AI
Provides tools for retrieving KYC rules, fraud patterns, and vector DB context
"""

import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import os
from datetime import datetime

# Set logging level from environment, default to WARNING to reduce noise
log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.WARNING))

# Suppress ChromaDB telemetry noisy logs
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)
logging.getLogger('chromadb').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Custom JSON encoder to handle ChromaDB objects
class ChromaDBSafeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            # Try the default encoder first
            return super().default(obj)
        except TypeError:
            # If it fails, try to convert to a safe representation
            if hasattr(obj, '__dict__'):
                return str(obj)
            elif hasattr(obj, 'items'):
                return dict(obj)
            else:
                return str(obj)

# Try to import chromadb for vector database
try:
    import chromadb
    CHROMADB_AVAILABLE = True  # Re-enable ChromaDB with proper handling
except ImportError:
    CHROMADB_AVAILABLE = False

app = FastAPI(
    title="KYC MCP Server",
    description="Model Context Protocol server for KYC tools",
    version="1.0.0"
)

# Configuration
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./kyc_vector_db")

# Initialize Chroma client if available
chroma_client = None
kyc_rules_collection = None
fraud_patterns_collection = None
historical_analysis_collection = None

if CHROMADB_AVAILABLE:
    try:
        # Initialize persistent Chroma client
        chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        
        # Create/get collections
        kyc_rules_collection = chroma_client.get_or_create_collection(
            name="kyc_rules",
            metadata={"hnsw:space": "cosine"}
        )
        
        fraud_patterns_collection = chroma_client.get_or_create_collection(
            name="fraud_patterns",
            metadata={"hnsw:space": "cosine"}
        )
        
        historical_analysis_collection = chroma_client.get_or_create_collection(
            name="historical_analysis",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info("✓ ChromaDB initialized successfully")
        logger.info(f"  - Vector DB Path: {VECTOR_DB_PATH}")
        logger.info(f"  - Collections: kyc_rules, fraud_patterns, historical_analysis")
        
    except Exception as e:
        logger.warning(f"Failed to initialize ChromaDB: {e}")
        CHROMADB_AVAILABLE = False
else:
    logger.warning("ChromaDB not available - falling back to in-memory storage")

# In-memory fallback storage
kyc_rules_storage = []
fraud_patterns_storage = []
historical_analysis_storage = []

# Pydantic Models
class RetrievalQuery(BaseModel):
    query: str
    document_type: Optional[str] = None
    country: Optional[str] = None
    top_k: int = 5

class MCPToolResult(BaseModel):
    tool_name: str
    status: str
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class KYCRule(BaseModel):
    rule_id: str
    title: str
    description: str
    document_type: str
    country: str
    requirement: str
    priority: str
    tags: List[str]

class FraudPattern(BaseModel):
    pattern_id: str
    pattern_name: str
    description: str
    indicators: List[str]
    risk_level: str
    detection_method: str
    tags: List[str]

# ═══════════════════════════════════════════════════════════════
# TOOL 1: Retrieve KYC Rules
# ═══════════════════════════════════════════════════════════════

def initialize_kyc_rules():
    """Initialize default KYC rules in vector DB"""
    default_rules = [
        {
            "rule_id": "rule_001",
            "title": "PAN Document Verification",
            "description": "Permanent Account Number must contain 10 alphanumeric characters with specific format: AAAAA0000A",
            "document_type": "PAN",
            "country": "India",
            "requirement": "First 5 characters are letters, next 4 are digits, last is letter",
            "priority": "CRITICAL",
            "tags": ["pan", "india", "tax_id", "format_validation"]
        },
        # PAN-ONLY SYSTEM: No additional generic rules needed
    ]
    
    if CHROMADB_AVAILABLE and kyc_rules_collection:
        for idx, rule in enumerate(default_rules):
            try:
                kyc_rules_collection.add(
                    ids=[rule["rule_id"]],
                    documents=[rule["description"]],
                    metadatas=[{
                        "title": rule["title"],
                        "document_type": rule["document_type"],
                        "country": rule["country"],
                        "requirement": rule["requirement"],
                        "priority": rule["priority"],
                        "tags": ",".join(rule["tags"])
                    }]
                )
            except Exception as e:
                logger.error(f"Failed to add rule {rule['rule_id']}: {e}")
    else:
        kyc_rules_storage.extend(default_rules)
    
    logger.info(f"✓ Initialized {len(default_rules)} KYC rules")

def initialize_fraud_patterns():
    """Initialize default fraud patterns in vector DB"""
    default_patterns = [
        {
            "pattern_id": "fraud_001",
            "pattern_name": "Document Tampering",
            "description": "Signs of physical alteration, erasure, or modification in document",
            "indicators": ["erasure_marks", "ink_inconsistency", "page_tears", "glue_residue"],
            "risk_level": "CRITICAL",
            "detection_method": "Visual inspection and metadata analysis",
            "tags": ["document_fraud", "tampering", "forgery"]
        },
        {
            "pattern_id": "fraud_002",
            "pattern_name": "Identity Mismatch",
            "description": "Inconsistencies between document photo and biometric data",
            "indicators": ["face_mismatch", "different_facial_features", "age_discrepancy"],
            "risk_level": "CRITICAL",
            "detection_method": "Facial recognition and biometric comparison",
            "tags": ["identity_fraud", "biometric_mismatch", "spoofing"]
        },
        {
            "pattern_id": "fraud_003",
            "pattern_name": "Duplicate/Synthetic Identity",
            "description": "Multiple applications using similar documents with slight variations",
            "indicators": ["similar_photo", "pattern_in_variations", "network_fraud"],
            "risk_level": "HIGH",
            "detection_method": "Database cross-referencing and pattern analysis",
            "tags": ["synthetic_identity", "duplicate_application", "network_fraud"]
        },
        {
            "pattern_id": "fraud_004",
            "pattern_name": "PII Data Leakage Indicators",
            "description": "Presence of unredacted sensitive PII in documents",
            "indicators": ["full_account_numbers", "unmasked_ssn", "exposed_passwords"],
            "risk_level": "HIGH",
            "detection_method": "OCR and regex pattern matching",
            "tags": ["data_leakage", "pii_exposure", "security_risk"]
        },
        {
            "pattern_id": "fraud_005",
            "pattern_name": "Document Age Anomaly",
            "description": "Document issue/expiry dates that don't make logical sense",
            "indicators": ["future_issue_date", "invalid_expiry", "reversed_dates"],
            "risk_level": "MEDIUM",
            "detection_method": "Date validation and temporal analysis",
            "tags": ["date_fraud", "temporal_anomaly", "document_integrity"]
        },
        {
            "pattern_id": "fraud_006",
            "pattern_name": "Behavioral Red Flags",
            "description": "Unusual submission patterns suggesting automated fraud",
            "indicators": ["rapid_submissions", "vpn_usage", "multiple_devices", "unusual_location"],
            "risk_level": "MEDIUM",
            "detection_method": "Behavior analysis and metadata review",
            "tags": ["behavioral_fraud", "automation_risk", "suspicious_activity"]
        },
        {
            "pattern_id": "fraud_007",
            "pattern_name": "Known Fraudster Pattern",
            "description": "Matching known fraud ring patterns or watchlist entries",
            "indicators": ["watchlist_match", "known_fraud_ring", "blacklisted_id"],
            "risk_level": "CRITICAL",
            "detection_method": "Database lookup and pattern matching",
            "tags": ["watchlist", "fraud_ring", "known_fraudster"]
        },
        {
            "pattern_id": "fraud_008",
            "pattern_name": "Unusual Transaction Pattern",
            "description": "Transaction history showing suspicious money flow patterns",
            "indicators": ["sudden_large_transfers", "circular_transfers", "structured_deposits"],
            "risk_level": "HIGH",
            "detection_method": "Transaction analysis and correlation",
            "tags": ["transaction_fraud", "money_laundering", "suspicious_activity"]
        }
    ]
    
    if CHROMADB_AVAILABLE and fraud_patterns_collection:
        for pattern in default_patterns:
            try:
                fraud_patterns_collection.add(
                    ids=[pattern["pattern_id"]],
                    documents=[pattern["description"]],
                    metadatas=[{
                        "pattern_name": pattern["pattern_name"],
                        "risk_level": pattern["risk_level"],
                        "indicators": ",".join(pattern["indicators"]),
                        "detection_method": pattern["detection_method"],
                        "tags": ",".join(pattern["tags"])
                    }]
                )
            except Exception as e:
                logger.error(f"Failed to add pattern {pattern['pattern_id']}: {e}")
    else:
        fraud_patterns_storage.extend(default_patterns)
    
    logger.info(f"✓ Initialized {len(default_patterns)} fraud patterns")

@app.post("/retrieve_kyc_rules", response_model=MCPToolResult)
async def retrieve_kyc_rules(query: RetrievalQuery) -> MCPToolResult:
    """
    MCP Tool: Retrieve KYC rules based on query
    
    Supports filtering by:
    - Document type (PAN, Aadhar, Passport, etc.)
    - Country
    - Free text search
    """
    logger.info(f"🔍 Retrieving KYC rules: query='{query.query}'")
    
    results = []
    
    try:
        if CHROMADB_AVAILABLE and kyc_rules_collection:
            # Query vector DB
            query_result = kyc_rules_collection.query(
                query_texts=[query.query],
                n_results=query.top_k,
                where_document=None
            )
            
            # Extract results safely
            ids = query_result.get("ids", [[]])
            metadatas = query_result.get("metadatas", [[]])
            documents = query_result.get("documents", [[]])
            distances = query_result.get("distances", [[]])
            
            for i in range(len(ids[0]) if ids and len(ids) > 0 else 0):
                try:
                    metadata = metadatas[0][i] if metadatas and len(metadatas) > 0 and i < len(metadatas[0]) else {}
                    document = documents[0][i] if documents and len(documents) > 0 and i < len(documents[0]) else ""
                    distance = distances[0][i] if distances and len(distances) > 0 and i < len(distances[0]) else None
                    
                    # Safely extract metadata as plain dict
                    metadata_dict = {}
                    if metadatas and len(metadatas) > 0 and i < len(metadatas[0]):
                        raw_metadata = metadatas[0][i]
                        if isinstance(raw_metadata, dict):
                            metadata_dict = raw_metadata.copy()  # Create a copy to avoid reference issues
                        elif hasattr(raw_metadata, 'items'):
                            try:
                                metadata_dict = dict(raw_metadata)  # Convert to plain dict
                            except Exception:
                                metadata_dict = {}
                    
                    result_item = {
                        "rule_id": str(ids[0][i]) if ids and len(ids) > 0 and i < len(ids[0]) else "",
                        "title": str(metadata_dict.get("title", "")),
                        "description": str(document),
                        "document_type": str(metadata_dict.get("document_type", "")),
                        "country": str(metadata_dict.get("country", "")),
                        "requirement": str(metadata_dict.get("requirement", "")),
                        "priority": str(metadata_dict.get("priority", "")),
                        "distance": float(distance) if distance is not None and str(distance).replace('.', '').isdigit() else None
                    }
                    
                    results.append(result_item)
                except Exception as e:
                    logger.warning(f"Error processing KYC rule result {i}: {e}")
                    continue
        else:
            # Fallback to in-memory search
            for rule in kyc_rules_storage:
                # Text matching
                if query.query.lower() in rule["description"].lower() or \
                   query.query.lower() in rule["title"].lower():
                    
                    # Apply filters
                    if query.document_type and rule["document_type"] != query.document_type:
                        continue
                    if query.country and rule["country"] != query.country:
                        continue
                    
                    results.append(rule)
                    
                    if len(results) >= query.top_k:
                        break
        
        logger.info(f"  ✓ Retrieved {len(results)} KYC rules")
        
        return MCPToolResult(
            tool_name="retrieve_kyc_rules",
            status="success",
            results=results,
            metadata={
                "query": query.query,
                "document_type_filter": query.document_type,
                "country_filter": query.country,
                "results_count": len(results),
                "vector_db_enabled": CHROMADB_AVAILABLE
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving KYC rules: {e}")
        return MCPToolResult(
            tool_name="retrieve_kyc_rules",
            status="error",
            results=[],
            metadata={"error": str(e)}
        )

@app.post("/retrieve_fraud_patterns", response_model=MCPToolResult)
async def retrieve_fraud_patterns(query: RetrievalQuery) -> MCPToolResult:
    """
    MCP Tool: Retrieve fraud patterns based on query
    
    Returns matching fraud patterns with:
    - Pattern indicators
    - Risk levels
    - Detection methods
    """
    logger.info(f"🚨 Retrieving fraud patterns: query='{query.query}'")
    
    results = []
    
    try:
        if CHROMADB_AVAILABLE and fraud_patterns_collection:
            # Query vector DB
            query_result = fraud_patterns_collection.query(
                query_texts=[query.query],
                n_results=query.top_k
            )
            
            # Extract results safely
            ids = query_result.get("ids", [[]])
            metadatas = query_result.get("metadatas", [[]])
            documents = query_result.get("documents", [[]])
            distances = query_result.get("distances", [[]])
            
            for i in range(len(ids[0]) if ids and len(ids) > 0 else 0):
                try:
                    metadata = metadatas[0][i] if metadatas and len(metadatas) > 0 and i < len(metadatas[0]) else {}
                    document = documents[0][i] if documents and len(documents) > 0 and i < len(documents[0]) else ""
                    distance = distances[0][i] if distances and len(distances) > 0 and i < len(distances[0]) else None
                    
                    # Safely extract metadata as plain dict
                    metadata_dict = {}
                    if metadatas and len(metadatas) > 0 and i < len(metadatas[0]):
                        raw_metadata = metadatas[0][i]
                        if isinstance(raw_metadata, dict):
                            metadata_dict = raw_metadata.copy()  # Create a copy to avoid reference issues
                        elif hasattr(raw_metadata, 'items'):
                            try:
                                metadata_dict = dict(raw_metadata)  # Convert to plain dict
                            except Exception:
                                metadata_dict = {}
                    
                    result_item = {
                        "pattern_id": str(ids[0][i]) if ids and len(ids) > 0 and i < len(ids[0]) else "",
                        "pattern_name": str(metadata_dict.get("pattern_name", "")),
                        "description": str(document),
                        "indicators": str(metadata_dict.get("indicators", "")).split(",") if metadata_dict.get("indicators") else [],
                        "risk_level": str(metadata_dict.get("risk_level", "")),
                        "detection_method": str(metadata_dict.get("detection_method", "")),
                        "distance": float(distance) if distance is not None and str(distance).replace('.', '').isdigit() else None
                    }
                    
                    results.append(result_item)
                except Exception as e:
                    logger.warning(f"Error processing fraud pattern result {i}: {e}")
                    continue
        else:
            # Fallback to in-memory search
            for pattern in fraud_patterns_storage:
                if query.query.lower() in pattern["description"].lower() or \
                   query.query.lower() in pattern["pattern_name"].lower():
                    results.append(pattern)
                    if len(results) >= query.top_k:
                        break
        
        logger.info(f"  ✓ Retrieved {len(results)} fraud patterns")
        
        return MCPToolResult(
            tool_name="retrieve_fraud_patterns",
            status="success",
            results=results,
            metadata={
                "query": query.query,
                "results_count": len(results),
                "vector_db_enabled": CHROMADB_AVAILABLE
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving fraud patterns: {e}")
        return MCPToolResult(
            tool_name="retrieve_fraud_patterns",
            status="error",
            results=[],
            metadata={"error": str(e)}
        )

@app.post("/retrieve_from_vector_db", response_model=MCPToolResult)
async def retrieve_from_vector_db(query: RetrievalQuery) -> MCPToolResult:
    """
    MCP Tool: Generic vector DB retrieval
    
    Searches across all collections:
    - KYC rules
    - Fraud patterns
    - Historical analysis
    """
    logger.info(f"🔎 Vector DB search: query='{query.query}'")
    
    all_results = {
        "kyc_rules": [],
        "fraud_patterns": [],
        "historical_analysis": []
    }
    
    try:
        if CHROMADB_AVAILABLE:
            # Search KYC rules
            kyc_results = kyc_rules_collection.query(
                query_texts=[query.query],
                n_results=min(3, query.top_k)
            )
            all_results["kyc_rules"] = [
                {"id": id_, "text": doc}
                for id_, doc in zip(
                    kyc_results["ids"][0] if kyc_results["ids"] else [],
                    kyc_results["documents"][0] if kyc_results["documents"] else []
                )
            ]
            
            # Search fraud patterns
            fraud_results = fraud_patterns_collection.query(
                query_texts=[query.query],
                n_results=min(3, query.top_k)
            )
            all_results["fraud_patterns"] = [
                {"id": id_, "text": doc}
                for id_, doc in zip(
                    fraud_results["ids"][0] if fraud_results["ids"] else [],
                    fraud_results["documents"][0] if fraud_results["documents"] else []
                )
            ]
        
        results = []
        for category, items in all_results.items():
            for item in items:
                results.append({
                    "category": category,
                    "id": item["id"],
                    "content": item["text"]
                })
        
        logger.info(f"  ✓ Retrieved {len(results)} results from vector DB")
        
        return MCPToolResult(
            tool_name="retrieve_from_vector_db",
            status="success",
            results=results,
            metadata={
                "query": query.query,
                "total_results": len(results),
                "by_category": {k: len(v) for k, v in all_results.items()},
                "vector_db_enabled": CHROMADB_AVAILABLE
            }
        )
        
    except Exception as e:
        logger.error(f"Error in vector DB retrieval: {e}")
        return MCPToolResult(
            tool_name="retrieve_from_vector_db",
            status="error",
            results=[],
            metadata={"error": str(e)}
        )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "retrieve_kyc_rules",
                "description": "Retrieve KYC compliance rules by query, document type, or country",
                "endpoint": "/retrieve_kyc_rules",
                "method": "POST",
                "parameters": {
                    "query": "Search query string",
                    "document_type": "Filter by document type (optional)",
                    "country": "Filter by country (optional)",
                    "top_k": "Number of results to return (default: 5)"
                }
            },
            {
                "name": "retrieve_fraud_patterns",
                "description": "Retrieve fraud detection patterns and indicators",
                "endpoint": "/retrieve_fraud_patterns",
                "method": "POST",
                "parameters": {
                    "query": "Search query string",
                    "top_k": "Number of results to return (default: 5)"
                }
            },
            {
                "name": "retrieve_from_vector_db",
                "description": "Generic vector database retrieval across all collections",
                "endpoint": "/retrieve_from_vector_db",
                "method": "POST",
                "parameters": {
                    "query": "Search query string",
                    "top_k": "Number of results to return (default: 5)"
                }
            }
        ]
    }

@app.post("/initialize")
async def initialize_db():
    """Manually initialize the vector database"""
    logger.info("═══════════════════════════════════════════════════════")
    logger.info("Initializing Vector Database")
    logger.info("═══════════════════════════════════════════════════════")
    
    initialize_kyc_rules()
    initialize_fraud_patterns()
    
    return {
        "status": "success",
        "message": "Vector database initialized successfully",
        "kyc_rules_count": len(kyc_rules_storage) if kyc_rules_storage else 0,
        "fraud_patterns_count": len(fraud_patterns_storage) if fraud_patterns_storage else 0,
        "vector_db_enabled": CHROMADB_AVAILABLE
    }

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    logger.info("═══════════════════════════════════════════════════════")
    logger.info("Starting MCP Server")
    logger.info("═══════════════════════════════════════════════════════")
    
    initialize_kyc_rules()
    initialize_fraud_patterns()
    
    logger.info("✓ MCP Server ready")

def safe_metadata_to_dict(metadata):
    """Safely convert ChromaDB metadata to plain dict"""
    try:
        if hasattr(metadata, 'items'):  # dict-like object
            return {str(k): str(v) for k, v in metadata.items()}
        elif isinstance(metadata, dict):
            return {str(k): str(v) for k, v in metadata.items()}
        else:
            return {}
    except Exception:
        return {}

def safe_get_metadata_field(metadata, key, default=""):
    """Safely get a field from metadata"""
    try:
        safe_metadata = safe_metadata_to_dict(metadata)
        value = safe_metadata.get(key, default)
        # Ensure the value is a basic type
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        else:
            return str(value)
    except Exception:
        return default
