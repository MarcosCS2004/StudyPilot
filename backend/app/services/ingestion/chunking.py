"""
Word-based chunking: chunk_size words with overlap sliding window.
Word-level (not token-level) — close enough for 512-token target at ~1.3 words/token average.
"""


class ChunkingService:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping word-based chunks."""
        words = text.split()
        if not words:
            return []

        chunks: list[str] = []
        step = max(1, self.chunk_size - self.overlap)
        i = 0
        while i < len(words):
            chunk_words = words[i : i + self.chunk_size]
            chunks.append(" ".join(chunk_words))
            i += step

        return chunks

    def chunk_with_metadata(self, text: str, metadata: dict) -> list[dict]:
        """Chunk text and attach metadata to each chunk dict."""
        texts = self.chunk_text(text)
        return [
            {"text": t, **metadata, "chunk_index": idx}
            for idx, t in enumerate(texts)
            if t.strip()
        ]
