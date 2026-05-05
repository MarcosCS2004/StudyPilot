"""
DualRAGOrchestrator — merges two context layers before LLM calls.

Layer 1 (domain knowledge): semantic search over the student's indexed notes in Qdrant.
Layer 2 (student memory): recent error history and weak topics from PostgreSQL.

The merged context dict maps directly to QUESTION_USER and AUTOPSY_USER format fields.
"""
from __future__ import annotations
from app.services.ai.embeddings import EmbeddingService
from app.services.ai.vector_store import VectorStoreClient
from app.core.config import settings


class DualRAGOrchestrator:
    def __init__(self):
        self.embedder = EmbeddingService(api_key=settings.AZURE_API_KEY or "")
        self.vector_store = VectorStoreClient(
            endpoint=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if hasattr(settings, "QDRANT_API_KEY") else None,
        )

    async def retrieve_context(
        self,
        topic: str,
        user_id: str,
        difficulty: int = 5,
        top_k: int = 5,
    ) -> dict:
        """
        Returns context dict with keys matching QUESTION_USER format fields:
        - chunks_from_notes: joined text from Qdrant (Layer 1)
        - errores_recientes: recent mistake descriptions from DB (Layer 2)
        """
        # Layer 1 — domain knowledge from notes
        try:
            topic_embedding = await self.embedder.embed_text(topic)
            domain_hits = await self.vector_store.search(
                query_embedding=topic_embedding,
                top_k=top_k,
                filters={"user_id": user_id, "difficulty_max": difficulty + 2},
            )
            import random
            # Mezclamos y tomamos una muestra para dar variedad a las preguntas
            all_chunks = [h.get("text", "") for h in domain_hits if h.get("text")]
            random.shuffle(all_chunks)
            # Tomamos máximo 3 chunks para que no se repita siempre el mismo contexto largo
            sample_chunks = all_chunks[:3]
            chunks_text = "\n---\n".join(sample_chunks)
        except Exception:
            chunks_text = "(Notes not available — vector store unreachable)"

        # Layer 2 — student memory (lazy import avoids circular deps with DB models)
        errores_text = "None on record"
        try:
            from app.services.error_history import ErrorHistoryService
            recent = await ErrorHistoryService.get_recent(user_id, topic, limit=3)
            if recent:
                errores_text = "; ".join(e.get("descripcion", "") for e in recent)
        except Exception:
            pass  # DB not connected yet — graceful degradation

        return {
            "chunks_from_notes": chunks_text or "(No notes indexed for this topic yet)",
            "errores_recientes": errores_text,
        }

    async def has_documents(self, user_id: str) -> bool:
        """Checks if the user has any materials uploaded."""
        return await self.vector_store.has_documents(user_id)

    async def delete_all_user_data(self, user_id: str) -> None:
        """Cleans up all user RAG data."""
        await self.vector_store.delete_user_chunks(user_id)

    async def delete_document_data(self, document_id: str) -> None:
        """Cleans up RAG data for a specific document."""
        await self.vector_store.delete_document_chunks(document_id)

    async def retrieve_autopsy_context(
        self,
        failed_topics: list[str],
        user_id: str,
        top_k_per_topic: int = 3,
    ) -> str:
        """
        Retrieves note chunks for multiple topics (exam autopsy).
        Returns single joined string for AUTOPSY_USER notes_chunks field.
        """
        all_chunks: list[str] = []
        for topic in failed_topics[:6]:  # cap at 6 topics to stay within context
            try:
                embedding = await self.embedder.embed_text(topic)
                hits = await self.vector_store.search(
                    query_embedding=embedding,
                    top_k=top_k_per_topic,
                    filters={"user_id": user_id},
                )
                all_chunks.extend(h.get("text", "") for h in hits)
            except Exception:
                pass

        if not all_chunks:
            # Fallback: get any notes for this user if nothing specific found
            try:
                hits = await self.vector_store.search(
                    query_embedding=[0.0] * self.vector_store.DIMS, # Dummy embedding for unfiltered search
                    top_k=10,
                    filters={"user_id": user_id},
                )
                all_chunks.extend(h.get("text", "") for h in hits)
            except Exception:
                pass

        if not all_chunks:
            return "(No relevant notes found in your collection. Please upload study materials related to this exam first.)"
        return "\n---\n".join(all_chunks)


dual_rag = DualRAGOrchestrator()
