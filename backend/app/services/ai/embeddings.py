"""
Azure OpenAI embeddings using text-embedding-3-large (1536 dims).
"""
import random
from openai import AsyncAzureOpenAI
from app.core.config import settings


class EmbeddingService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if not api_key:
            print("WARNING: EMBEDDING_SERVICE: No API Key found. Running in MOCK MODE.")
            self._client = None
        else:
            self._client = AsyncAzureOpenAI(
                azure_endpoint=settings.AZURE_ENDPOINT or "https://placeholder.openai.azure.com",
                api_key=api_key,
                api_version="2024-02-01",
            )
        self.model = settings.EMBEDDING_MODEL  # "text-embedding-3-large"

    async def embed_text(self, text: str) -> list[float]:
        """Generate 1536-dim embedding for a single text string."""
        if not self._client:
            # Return a mock vector of 1536 dimensions
            return [random.uniform(-1, 1) for _ in range(1536)]

        resp = await self._client.embeddings.create(
            input=text[:8000],  # model token limit safety
            model=self.model,
        )
        return resp.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch. Returns list in same order as input."""
        if not self._client:
            return [[random.uniform(-1, 1) for _ in range(1536)] for _ in texts]

        truncated = [t[:8000] for t in texts]
        resp = await self._client.embeddings.create(
            input=truncated,
            model=self.model,
        )
        # API returns results sorted by index
        return [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]
