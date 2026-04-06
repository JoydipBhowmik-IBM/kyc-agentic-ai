"""
Integration Example: Using Mock Validation API with Verify Agent

This shows how to integrate the mock validation API into the verify agent
"""

from typing import Optional, Dict, Any

# Option 1: Direct Import (if in same service)
# ============================================
# from mock_validation_api import MockPANValidator, validate_pan_mock

# Option 2: HTTP Request (if running as separate service)
# ========================================================
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MOCK_API_URL = "http://localhost:8001"  # Mock validation service URL


class VerifyAgentWithMockAPI:
    """
    Verify Agent integration with Mock PAN Validation API
    """
    
    def __init__(self, use_mock: bool = True):
        """
        Initialize verify agent with optional mock API
        
        Args:
            use_mock: If True, use mock API. If False, use real API (when available)
        """
        self.use_mock = use_mock
        self.mock_api_url = MOCK_API_URL
    
    def verify_pan_with_mock(self, pan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify PAN using mock validation API
        
        Args:
            pan_data: Dictionary with keys:
                - pan_number: str
                - name: str (optional)
                - father_name: str (optional)
                - dob: str (optional)
        
        Returns:
            Validation response dictionary
        """
        try:
            if not self.use_mock:
                logger.warning("Mock API disabled. Would use real API here.")
                return None
            
            pan_number = pan_data.get("pan_number")
            name = pan_data.get("name")
            dob = pan_data.get("dob")
            
            logger.info(f"🔍 Mock verifying PAN: {pan_number}")
            
            # Call mock validation API
            response = requests.post(
                f"{self.mock_api_url}/validate-pan",
                json={
                    "pan_number": pan_number,
                    "name": name,
                    "dob": dob
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Validation result: {result['status']} (Confidence: {result['confidence']})")
                return result
            else:
                logger.error(f"❌ Validation failed: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Could not connect to mock API at {self.mock_api_url}")
            return None
        except Exception as e:
            logger.error(f"❌ Error during mock verification: {str(e)}")
            return None
    
    def batch_verify_with_mock(self, pan_list: list) -> Dict[str, Any]:
        """
        Verify multiple PANs using mock API
        
        Args:
            pan_list: List of PAN numbers
        
        Returns:
            Batch validation results
        """
        try:
            logger.info(f"🔍 Mock batch verifying {len(pan_list)} PANs")
            
            response = requests.post(
                f"{self.mock_api_url}/batch-validate",
                json={"pan_list": pan_list},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Batch verification complete: {result['summary']}")
                return result
            else:
                logger.error(f"❌ Batch verification failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error during batch verification: {str(e)}")
            return None
    
    def get_test_cases(self) -> Dict[str, str]:
        """Get available test cases from mock API"""
        try:
            response = requests.get(
                f"{self.mock_api_url}/test-cases",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("test_cases", {})
            
        except Exception as e:
            logger.error(f"Error fetching test cases: {str(e)}")
        
        return {}


# ============================================================
# ALTERNATIVE: Direct Import (for use within same service)
# ============================================================

class VerifyAgentWithDirectImport:
    """
    Alternative: Direct import of mock validator
    Use this if verify-agent has mock_validation_api.py in same directory
    """
    
    def __init__(self):
        """Initialize with direct import"""
        try:
            from mock_validation_api import MockPANValidator
            self.validator = MockPANValidator()
            self.use_mock = True
        except ImportError:
            self.validator = None
            self.use_mock = False
            logger.warning("Could not import MockPANValidator")
    
    def verify_pan(self, pan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify PAN using direct import"""
        if not self.use_mock or not self.validator:
            logger.error("Mock validator not available")
            return None
        
        try:
            pan_number = pan_data.get("pan_number")
            name = pan_data.get("name")
            dob = pan_data.get("dob")
            
            logger.info(f"🔍 Verifying PAN: {pan_number}")
            
            result = self.validator.validate_pan(
                pan_number=pan_number,
                name=name,
                dob=dob
            )
            
            logger.info(f"✅ Result: {result['status']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Verification error: {str(e)}")
            return None


# ============================================================
# EXAMPLE USAGE
# ============================================================

def example_usage():
    """
    Example usage of mock validation API with verify agent
    """
    
    print("\n" + "="*70)
    print("MOCK VALIDATION API - VERIFY AGENT INTEGRATION")
    print("="*70)
    
    # Your PAN data
    your_pan_data = {
        "pan_number": "CYMPB5839A",
        "name": "BORUGULA SURESH",
        "father_name": "BORUGULA MUNASWAMY",
        "dob": "06/03/1992"
    }
    
    # Initialize verify agent with mock API
    verify_agent = VerifyAgentWithMockAPI(use_mock=True)
    
    # Example 1: Verify your PAN
    print("\n✅ Example 1: Verify Your PAN")
    print("-" * 70)
    print(f"Input: {your_pan_data}")
    
    result = verify_agent.verify_pan_with_mock(your_pan_data)
    
    if result:
        print(f"\nResult:")
        print(f"  Status: {result['status']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Reason: {result['details']['reason']}")
        print(f"  Checks Passed: {len(result['details']['checks_passed'])}")
        print(f"  Checks Failed: {len(result['details']['checks_failed'])}")
    
    # Example 2: Batch verification
    print("\n" + "="*70)
    print("✅ Example 2: Batch Verify Multiple PANs")
    print("-" * 70)
    
    test_pans = [
        "CYMPB5839A",      # Valid
        "SAMPLE123X",      # Watermarked
        "ABCDE1234F",      # Valid
        "INVALID123",      # Invalid format
    ]
    
    print(f"Testing PANs: {test_pans}\n")
    
    batch_result = verify_agent.batch_verify_with_mock(test_pans)
    
    if batch_result:
        print(f"Summary:")
        print(f"  Total: {batch_result['total']}")
        print(f"  Approved: {batch_result['summary']['approved']}")
        print(f"  Rejected: {batch_result['summary']['rejected']}")
        print(f"  Approval Rate: {batch_result['summary']['approval_rate']}")
    
    # Example 3: Get test cases
    print("\n" + "="*70)
    print("✅ Example 3: Available Test Cases")
    print("-" * 70)
    
    test_cases = verify_agent.get_test_cases()
    
    print(f"\nAvailable test cases:")
    for pan, status in test_cases.items():
        print(f"  {pan:<15} → {status}")
    
    print("\n" + "="*70)
    print("Integration examples complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run examples
    example_usage()
    
    print("\n📝 INTEGRATION STEPS:")
    print("-" * 70)
    print("1. Start mock API service:")
    print("   python -m uvicorn mock_validation_endpoint:app --port 8001")
    print()
    print("2. Use in verify-agent:")
    print("   from mock_validation_integration import VerifyAgentWithMockAPI")
    print("   agent = VerifyAgentWithMockAPI(use_mock=True)")
    print("   result = agent.verify_pan_with_mock(pan_data)")
    print()
    print("3. Or import directly:")
    print("   from mock_validation_api import MockPANValidator")
    print("   validator = MockPANValidator()")
    print("   result = validator.validate_pan(pan_number)")
    print("-" * 70)
