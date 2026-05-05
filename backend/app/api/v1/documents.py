from fastapi import APIRouter, File, Form, UploadFile, Depends
from typing import Optional

from app.core.config import settings
from app.schemas.api import UploadResponse
from app.services.ai.embeddings import EmbeddingService
from app.services.ai.llm_client import llm_client
from app.services.ai.vector_store import VectorStoreClient
from app.services.ingestion.chunking import ChunkingService
from app.services.ai.prompts import CHUNK_CLASSIFY_SYSTEM, CHUNK_CLASSIFY_USER
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "image/jpeg",
    "image/png",
    "text/plain",
}

_embedder = EmbeddingService(api_key=settings.AZURE_API_KEY or "")
_vector_store = VectorStoreClient(
    endpoint=settings.QDRANT_URL,
    api_key=settings.AZURE_API_KEY or "",
)
_chunker = ChunkingService(
    chunk_size=settings.RAG_CHUNK_SIZE,
    overlap=settings.RAG_CHUNK_OVERLAP,
)

@router.get("/")
async def get_documents(current_user: User = Depends(get_current_user)):
    """Returns list of uploaded documents for the current user."""
    return _vector_store.get_mock_documents(current_user.id)

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    asignatura: str = Form(default="General"),
    current_user: User = Depends(get_current_user),
):
    """
    Indexes a study document into the vector store for RAG retrieval.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        return UploadResponse(
            file_id="",
            status="error",
            mensaje=f"Unsupported file type: {file.content_type}",
        )

    content = await file.read()
    file_size_kb = len(content) // 1024

    # Step 1: Extract text
    extracted_text = ""
    if file.content_type == "application/pdf":
        try:
            import io
            from pypdf import PdfReader
            pdf = PdfReader(io.BytesIO(content))
            extracted_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            print(f"DEBUG: Extracted {len(extracted_text)} chars from PDF.")
        except Exception as e:
            print(f"ERROR: PDF extraction failed: {e}")
    
    if not extracted_text:
        try:
            extracted_text = content.decode("utf-8")
        except:
            extracted_text = content.decode("latin-1", errors="ignore")

    if not extracted_text.strip():
        return UploadResponse(
            file_id="",
            status="error",
            mensaje=f"Could not extract text from {file.filename}. Check if it's a valid document.",
        )

    # Step 2: Chunk
    import uuid
    file_id = str(uuid.uuid4())
    chunks = _chunker.chunk_with_metadata(
        extracted_text,
        metadata={
            "user_id": str(current_user.id),
            "asignatura": asignatura,
            "document_id": file_id,
            "filename": file.filename
        },
    )

    if not chunks:
        return UploadResponse(
            file_id=file_id,
            status="done",
            mensaje=f"'{file.filename}' yielded no chunks.",
        )

    # Step 3: Embed
    texts = [c["text"] for c in chunks]
    embeddings = await _embedder.embed_batch(texts)
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb

    # Step 3.5: Auto-classify chunks (Parallelized)
    import asyncio
    
    # Limit concurrency to avoid hitting rate limits or overwhelming the server
    semaphore = asyncio.Semaphore(15)
    
    async def classify_chunk(chunk):
        async with semaphore:
            try:
                classify_prompt = CHUNK_CLASSIFY_USER.format(
                    filename=file.filename or "unknown",
                    page=chunk.get("chunk_index", 0) + 1,
                    chunk_text=chunk["text"][:1500],
                )
                classification = await llm_client.generate_json(
                    CHUNK_CLASSIFY_SYSTEM, classify_prompt
                )
                chunk["topic"] = classification.get("topic", "")
                chunk["subject"] = classification.get("subject", asignatura)
                chunk["difficulty"] = classification.get("difficulty", 5)
            except Exception as e:
                print(f"DEBUG: Classification failed for chunk {chunk.get('chunk_index')}: {e}")
                chunk["topic"] = ""
                chunk["subject"] = asignatura
                chunk["difficulty"] = 5

    # If the document is massive, only classify a representative sample to keep it fast
    # A 4MB PDF can have hundreds of chunks. We classify up to 50.
    MAX_CLASSIFY = 50
    if len(chunks) > MAX_CLASSIFY:
        print(f"DEBUG: Large document ({len(chunks)} chunks). Classifying sample of {MAX_CLASSIFY}.")
        # Sample chunks across the document
        indices = [int(i * (len(chunks) - 1) / (MAX_CLASSIFY - 1)) for i in range(MAX_CLASSIFY)]
        chunks_to_classify = [chunks[i] for i in indices]
    else:
        chunks_to_classify = chunks

    await asyncio.gather(*(classify_chunk(c) for c in chunks_to_classify))

    # Ensure all chunks have the required fields even if not classified
    for chunk in chunks:
        if "topic" not in chunk:
            chunk["topic"] = ""
            chunk["subject"] = asignatura
            chunk["difficulty"] = 5

    # Step 4: Store
    await _vector_store.ensure_collection()
    await _vector_store.index_chunks(chunks)

    return UploadResponse(
        file_id=file_id,
        status="done",
        mensaje=f"'{file.filename}' indexed successfully: {len(chunks)} chunks stored."
    )

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Permanently deletes a document and its chunks."""
    from app.services.ai.dual_rag import dual_rag
    # We should probably verify ownership here, but for now we delete from vector store
    await dual_rag.delete_document_data(document_id)
    return None

@router.delete("/all", status_code=204)
async def delete_all_documents(
    current_user: User = Depends(get_current_user)
):
    """Deletes all documents for the current user."""
    from app.services.ai.dual_rag import dual_rag
    await dual_rag.delete_all_user_data(current_user.id)
    return None
