from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.llm_service import LLMService

class BillAgent(BaseAgent):
    """Agent specialized in processing medical bills"""
    
    def __init__(self, llm_service: LLMService):
        super().__init__("BillAgent")
        self.llm_service = llm_service
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process medical bill document
        
        Args:
            data: Dict containing document text and metadata
            
        Returns:
            Dict with extracted bill information
        """
        try:
            self.log_info("Processing medical bill document")
            
            text = data['text']
            
            # Extract structured data from bill
            extracted_data = await self.llm_service.extract_bill_data(text)
            
            # Validate extracted data
            validation_errors = self._validate_bill_data(extracted_data)
            
            result = {
                'type': 'bill',
                'extracted_data': extracted_data,
                'validation_errors': validation_errors,
                'processing_status': 'completed' if not validation_errors else 'completed_with_warnings'
            }
            
            self.log_info(f"Bill processing completed. Found {len(validation_errors)} validation issues")
            
            return result
            
        except Exception as e:
            self.log_error(f"Bill processing failed: {str(e)}")
            return {
                'type': 'bill',
                'extracted_data': {},
                'validation_errors': [f"Processing error: {str(e)}"],
                'processing_status': 'failed'
            }
    
    def _validate_bill_data(self, data: Dict[str, Any]) -> list:
        """Validate extracted bill data"""
        errors = []
        
        # Check for critical fields
        if not data.get('hospital_name'):
            errors.append("Hospital name not found")
        
        if not data.get('total_amount'):
            errors.append("Total amount not found")
        
        if not data.get('date_of_service'):
            errors.append("Date of service not found")
        
        # Validate amount format
        if data.get('total_amount') and not isinstance(data['total_amount'], (int, float)):
            errors.append("Invalid total amount format")
        
        return errors