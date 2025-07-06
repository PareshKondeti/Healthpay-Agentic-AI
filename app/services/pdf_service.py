import PyPDF2
import logging
from typing import Optional
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    async def extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """Extract text from PDF content asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _extract_text():
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                
                return text.strip()
            except Exception as e:
                logger.error(f"PDF text extraction error: {str(e)}")
                return None
        
        return await loop.run_in_executor(self.executor, _extract_text)
    
    def validate_pdf(self, pdf_content: bytes) -> bool:
        """Validate that the content is a valid PDF"""
        try:
            PyPDF2.PdfReader(io.BytesIO(pdf_content))
            return True
        except Exception as e:
            logger.error(f"PDF validation error: {str(e)}")
            return False