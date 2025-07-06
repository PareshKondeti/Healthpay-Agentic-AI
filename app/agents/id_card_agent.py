from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.llm_service import LLMService

class IDCardAgent(BaseAgent):
    """Agent specialized in processing insurance ID cards"""
    
    def __init__(self, llm_service: LLMService):
        super().__init__("IDCardAgent")
        self.llm_service = llm_service
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process insurance ID card document
        
        Args:
            data: Dict containing document text and metadata
            
        Returns:
            Dict with extracted ID card information
        """
        try:
            self.log_info("Processing insurance ID card document")
            
            text = data['text']
            
            # Extract structured data from ID card
            extracted_data = await self.llm_service.extract_id_card_data(text)
            
            # Validate extracted data
            validation_errors = self._validate_id_card_data(extracted_data)
            
            result = {
                'type': 'id_card',
                'extracted_data': extracted_data,
                'validation_errors': validation_errors,
                'processing_status': 'completed' if not validation_errors else 'completed_with_warnings'
            }
            
            self.log_info(f"ID card processing completed. Found {len(validation_errors)} validation issues")
            
            return result
            
        except Exception as e:
            self.log_error(f"ID card processing failed: {str(e)}")
            return {
                'type': 'id_card',
                'extracted_data': {},
                'validation_errors': [f"Processing error: {str(e)}"],
                'processing_status': 'failed'
            }
    
    def _validate_id_card_data(self, data: Dict[str, Any]) -> list:
        """Validate extracted ID card data"""
        errors = []
        
        # Check for critical fields
        if not data.get('patient_name'):
            errors.append("Patient name not found")
        
        if not data.get('insurance_id'):
            errors.append("Insurance ID not found")
        
        if not data.get('policy_number'):
            errors.append("Policy number not found")
        
        return errors