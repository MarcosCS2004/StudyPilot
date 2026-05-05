"""
Qdrant vector store client — index chunks and semantic search for RAG.
"""
import uuid
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)


class VectorStoreClient:
    COLLECTION = "studypilot_notes"
    DIMS = 1536  # text-embedding-3-large output dimensions
    _mock_storage = []  # Almacenamiento en memoria compartido
    _MOCK_FILE = "mock_vector_store.json"

    def __init__(self, endpoint: str, api_key: str):
        self._api_key = api_key
        self._endpoint = endpoint
        self._client = AsyncQdrantClient(url=endpoint, api_key=api_key or None)
        self._is_mock = False
        self._load_mock_data()

    def _load_mock_data(self):
        import json, os
        if os.path.exists(self._MOCK_FILE):
            try:
                with open(self._MOCK_FILE, "r") as f:
                    VectorStoreClient._mock_storage = json.load(f)
                    print(f"DEBUG: Loaded {len(VectorStoreClient._mock_storage)} chunks from {self._MOCK_FILE}")
            except Exception as e:
                print(f"ERROR loading mock data: {e}")

    def _save_mock_data(self):
        import json
        try:
            with open(self._MOCK_FILE, "w") as f:
                json.dump(VectorStoreClient._mock_storage, f)
        except Exception as e:
            print(f"ERROR saving mock data: {e}")

    async def _check_connection(self):
        try:
            # We skip real Qdrant check if we want to force MOCK during dev
            # or if it fails, we use mock.
            if self._endpoint == "http://mock":
                self._is_mock = True
                return False
            await self._client.get_collections()
            return True
        except Exception:
            if not self._is_mock:
                print(f"WARNING: VECTOR_STORE: Could not connect to Qdrant at {self._endpoint}. Running in MOCK MODE.")
                self._is_mock = True
            return False

    async def ensure_collection(self) -> None:
        """Create the notes collection if it does not already exist."""
        if not await self._check_connection():
            return

        existing = await self._client.get_collections()
        names = {c.name for c in existing.collections}
        if self.COLLECTION not in names:
            await self._client.create_collection(
                collection_name=self.COLLECTION,
                vectors_config=VectorParams(size=self.DIMS, distance=Distance.COSINE),
            )

    async def index_chunks(
        self, chunks: list[dict], collection_name: str | None = None
    ) -> None:
        """
        Upsert chunks into Qdrant.
        """
        if not await self._check_connection():
            print(f"DEBUG: MOCK_VECTOR_STORE: Indexing {len(chunks)} chunks.")
            # Guardamos los chunks en memoria
            for chunk in chunks:
                entry = {
                    "text": chunk.get("text", ""),
                    "user_id": str(chunk.get("user_id", "")),
                    "topic": chunk.get("topic", "General"),
                    "subject": chunk.get("subject", "General"),
                    "difficulty": chunk.get("difficulty", 5),
                    "document_id": chunk.get("document_id", ""),
                    "filename": chunk.get("filename", "unknown.pdf")
                }
                VectorStoreClient._mock_storage.append(entry)
                print(f"DEBUG: MOCK_STORAGE: Added chunk for user {entry['user_id']}. Total: {len(VectorStoreClient._mock_storage)}")
            self._save_mock_data()
            return

        col = collection_name or self.COLLECTION
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=chunk["embedding"],
                payload={
                    "text": chunk.get("text", ""),
                    "user_id": chunk.get("user_id", ""),
                    "topic": chunk.get("topic", ""),
                    "subject": chunk.get("subject", ""),
                    "difficulty": chunk.get("difficulty", 5),
                    "document_id": chunk.get("document_id", ""),
                    "chunk_index": chunk.get("chunk_index", 0),
                },
            )
            for chunk in chunks
            if "embedding" in chunk
        ]
        if points:
            await self._client.upsert(collection_name=col, points=points)

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[dict]:
        """
        Cosine similarity search. Returns list of payload dicts with added 'score' key.
        """
        if not await self._check_connection():
            user_id = str(filters.get("user_id")) if filters and filters.get("user_id") else None
            print(f"DEBUG: MOCK_VECTOR_STORE: Searching for user_id: {user_id}. Storage size: {len(VectorStoreClient._mock_storage)}")
            
            # Filtrar por usuario si es necesario
            valid_chunks = [c for c in VectorStoreClient._mock_storage if not user_id or str(c.get("user_id")) == user_id]
            print(f"DEBUG: MOCK_VECTOR_STORE: Found {len(valid_chunks)} valid chunks.")
            
            if valid_chunks:
                import random
                # Simulamos búsqueda aleatoria para dar variedad
                num_results = min(len(valid_chunks), top_k)
                results = random.sample(valid_chunks, num_results)
                for r in results:
                    r["score"] = 0.95
                return results
            else:
                return [
                    {
                        "text": "Este es un resultado de búsqueda simulado porque Qdrant no está disponible.",
                        "user_id": user_id or "",
                        "topic": "General",
                        "subject": "General",
                        "difficulty": 5,
                        "score": 0.99
                    }
                ]

        qdrant_filter = None
        if filters and "user_id" in filters:
            must_conditions: list = [
                FieldCondition(key="user_id", match=MatchValue(value=filters["user_id"]))
            ]
            if "difficulty_max" in filters:
                must_conditions.append(
                    FieldCondition(
                        key="difficulty",
                        range=Range(lte=filters["difficulty_max"]),
                    )
                )
            qdrant_filter = Filter(must=must_conditions)

        results = await self._client.search(
            collection_name=self.COLLECTION,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )
        return [{**hit.payload, "score": hit.score} for hit in results]

    def get_mock_documents(self, user_id: str) -> list[dict]:
        """Returns unique documents from mock storage for a user."""
        docs = {}
        for c in VectorStoreClient._mock_storage:
            if str(c.get("user_id")) == str(user_id):
                doc_id = c.get("document_id")
                if doc_id and doc_id not in docs:
                    docs[doc_id] = {
                        "id": doc_id,
                        "filename": c.get("filename"),
                        "subject": c.get("subject"),
                    }
        return list(docs.values())

    async def has_documents(self, user_id: str) -> bool:
        """Checks if a user has any indexed documents."""
        if not await self._check_connection():
            return any(str(c.get("user_id")) == str(user_id) for c in VectorStoreClient._mock_storage)
        
        try:
            res = await self._client.count(
                collection_name=self.COLLECTION,
                count_filter=Filter(
                    must=[FieldCondition(key="user_id", match=MatchValue(value=str(user_id)))]
                )
            )
            return res.count > 0
        except Exception:
            return False

    async def delete_user_chunks(self, user_id: str) -> None:
        """Deletes all chunks belonging to a user."""
        if not await self._check_connection():
            VectorStoreClient._mock_storage = [c for c in VectorStoreClient._mock_storage if str(c.get("user_id")) != str(user_id)]
            self._save_mock_data()
            return
        
        await self._client.delete(
            collection_name=self.COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=str(user_id)))]
            )
        )

    async def delete_document_chunks(self, document_id: str) -> None:
        """Deletes all chunks belonging to a specific document."""
        if not await self._check_connection():
            VectorStoreClient._mock_storage = [c for c in VectorStoreClient._mock_storage if str(c.get("document_id")) != str(document_id)]
            self._save_mock_data()
            return
        
        await self._client.delete(
            collection_name=self.COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=str(document_id)))]
            )
        )
