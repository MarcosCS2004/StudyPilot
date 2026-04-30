"""
Azure Document Intelligence (OCR)
"""

class DocumentParser:
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
    
    async def parse_document(self, file_path: str):
        """Parsear documento con OCR"""
        pass
    
    async def extract_text(self, file_path: str):
        """Extraer texto del documento"""
        pass
