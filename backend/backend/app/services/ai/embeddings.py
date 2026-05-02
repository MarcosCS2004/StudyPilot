"""
Integración con text-embedding-3-large (OpenAI)
"""

class EmbeddingService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "text-embedding-3-large"
    
    async def embed_text(self, text: str):
        """Generar embedding para texto"""
        pass
    
    async def embed_batch(self, texts: list):
        """Generar embeddings para lote de textos"""
        pass
