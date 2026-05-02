"""
Estrategia de chunking: 512 tokens + 64 overlap
"""

class ChunkingService:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> list:
        """Dividir texto en chunks"""
        pass
    
    def chunk_with_metadata(self, text: str, metadata: dict) -> list:
        """Dividir texto preservando metadata"""
        pass
