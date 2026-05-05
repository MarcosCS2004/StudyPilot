from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.ai.llm_client import llm_client
from app.services.ai.dual_rag import dual_rag

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    subject_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []

CHAT_SYSTEM_PROMPT = """\
Eres un tutor académico experto de StudyPilot. Tu misión es ayudar al estudiante a comprender sus materiales de estudio.

Reglas de comportamiento:
1. Responde SIEMPRE basándote en los fragmentos de apuntes proporcionados si son relevantes.
2. Si la respuesta no está en los apuntes, usa tu conocimiento general pero advierte al estudiante que es información externa.
3. Mantén un tono motivador, profesional y pedagógico.
4. Si el estudiante te pide que expliques algo "como si tuviera 5 años", usa analogías sencillas.
5. Si detectas que el estudiante tiene una duda sobre un concepto fundamental, intenta explicárselo paso a paso.

Contexto de los apuntes del alumno:
{context}

Responde en español (es-ES).
"""

@router.post("/", response_model=ChatResponse)
async def chat_with_tutor(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    # 1. Verificar si hay documentos. Si no, pedir subirlos.
    if not await dual_rag.has_documents(current_user.id):
        return ChatResponse(
            response="¡Hola! Todavía no tienes materiales de estudio subidos. Para poder ayudarte con tus dudas específicas, por favor sube tus apuntes en formato PDF en el apartado de 'Materiales'. ¡Estaré encantado de analizarlos contigo!",
            sources=[]
        )

    # 2. Recuperar contexto relevante de los apuntes usando RAG
    try:
        context_data = await dual_rag.retrieve_context(
            topic=request.message,
            user_id=current_user.id,
            top_k=4
        )
        context_text = context_data.get("chunks_from_notes", "No hay apuntes específicos sobre este tema todavía.")
    except Exception as e:
        context_text = "Error al recuperar apuntes. Respondiendo con conocimiento general."

    # 2. Preparar el historial para el modelo
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT.format(context=context_text)}]
    
    # Añadir historial (limitado a los últimos 6 mensajes para no saturar contexto)
    for msg in request.history[-6:]:
        messages.append({"role": msg.role, "content": msg.content})
    
    # Añadir mensaje actual
    messages.append({"role": "user", "content": request.message})

    # 3. Generar respuesta usando LLM
    try:
        # Usamos generate_text directamente para una respuesta conversacional
        # Pero como llm_client.generate_text no acepta historial arbitrario fácilmente, 
        # vamos a usar una pequeña adaptación o llamar al cliente de openai directamente si es necesario.
        # Por simplicidad en modo Mock, usaremos generate_text.
        
        system_final = CHAT_SYSTEM_PROMPT.format(context=context_text)
        response_text = await llm_client.generate_text(system_final, request.message)
        
        return ChatResponse(
            response=response_text,
            sources=[context_text[:200] + "..." ] if context_text else []
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
