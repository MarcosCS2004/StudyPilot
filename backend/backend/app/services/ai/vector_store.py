"""
Operaciones con Qdrant/Azure AI Search
"""

class VectorStoreClient:
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
    
    async def index_chunks(self, chunks: list, collection_name: str):
        """Indexar chunks de documentos"""
        pass
    
    async def search(self, query_embedding: list, top_k: int = 5):
        """Buscar vectores similares"""
        pass
