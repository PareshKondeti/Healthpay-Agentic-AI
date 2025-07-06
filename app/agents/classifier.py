from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.llm_service import LLMService

class ClassifierAgent(BaseAgent):
    """Agent responsible for classifying document types"""
    
    def __init__(self, llm_service: LLMService):
        super().__init__("ClassifierAgent")
        self.llm_service = llm_service
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify document type based on content and filename
        
        Args:
            data: Dict containing 'text' and 'filename'
            
        Returns:
            Dict with classification results
        """
        try:
            self.log_info(f"Classifying document: {data['filename']}")
            
            text = data['text']
            filename = data['filename']
            
            # Use LLM to classify document
            result = await self.llm_service.classify_document(text, filename)
            
            self.log_info(f"Classification result: {result['type']} (confidence: {result['confidence']})")
            
            return {
                'type': result['type'],
                'confidence': result['confidence'],
                'reasoning': result.get('reasoning', ''),
                'filename': filename
            }
            
        except Exception as e:
            self.log_error(f"Classification failed: {str(e)}")
            return {
                'type': 'unknown',
                'confidence': 0.0,
                'reasoning': f"Classification error: {str(e)}",
                'filename': data.get('filename', 'unknown')
            }