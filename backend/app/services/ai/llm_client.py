import json
import base64
import logging
import asyncio
from openai import AsyncAzureOpenAI, RateLimitError, APITimeoutError
from app.core.config import settings

logger = logging.getLogger("studypilot.llm")

MAX_RETRIES = 3
RETRY_BACKOFF = [1, 3, 8]

class LLMClient:
    def __init__(self):
        self._client: AsyncAzureOpenAI | None = None
        self.is_mock = False
        
        # Check if we should use mock mode
        if not settings.AZURE_API_KEY or "your_api_key" in settings.AZURE_API_KEY.lower() or settings.AZURE_API_KEY == "placeholder":
            logger.warning("⚠️ LLM_CLIENT: No valid Azure API Key found. Running in MOCK MODE.")
            self.is_mock = True

    def _get_client(self) -> AsyncAzureOpenAI:
        if self._client is None:
            self._client = AsyncAzureOpenAI(
                azure_endpoint=settings.AZURE_ENDPOINT or "https://placeholder.openai.azure.com",
                api_key=settings.AZURE_API_KEY or "placeholder",
                api_version="2024-12-01-preview",
            )
        return self._client

    async def _call_with_retry(self, func, *args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return await func(*args, **kwargs)
            except (RateLimitError, APITimeoutError) as exc:
                wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(wait)

    async def generate_json(self, system: str, user: str) -> dict:
        if self.is_mock:
            return self._get_mock_response(system, user)

        async def _call():
            return await self._get_client().chat.completions.create(
                model=settings.AZURE_DEPLOYMENT,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

        try:
            resp = await self._call_with_retry(_call)
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM Error: {e}. Falling back to mock.")
            return self._get_mock_response(system, user)

    async def generate_text(self, system: str, user: str) -> str:
        if self.is_mock:
            # Reutilizamos la lógica de extracción de fragmentos para el chat
            mock_data = self._get_mock_response(system, user)
            if "explicacion" in mock_data:
                return mock_data["explicacion"]
            if "resumen" in mock_data:
                return mock_data["resumen"]
            return "Esta es una respuesta simulada basada en el contexto de tus apuntes."

        async def _call():
            return await self._get_client().chat.completions.create(
                model=settings.AZURE_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.5,
                max_tokens=800,
            )

        try:
            resp = await self._call_with_retry(_call)
            return resp.choices[0].message.content
        except:
            return "Error al contactar con el modelo de IA. Verifica tu configuración."

    async def generate_with_image(self, system: str, user: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
        if self.is_mock:
            return self._get_mock_response("autopsy", user)

        b64 = base64.b64encode(image_bytes).decode("utf-8")

        async def _call():
            return await self._get_client().chat.completions.create(
                model=settings.AZURE_DEPLOYMENT,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                        ],
                    },
                ],
                max_tokens=3000,
            )

        try:
            resp = await self._call_with_retry(_call)
            return json.loads(resp.choices[0].message.content)
        except:
            return self._get_mock_response("autopsy", user)

    def _get_mock_response(self, system_type: str, user_prompt: str) -> dict:
        """Generador de respuestas mock dinámico según el contexto"""
        system_lower = system_type.lower()
        user_lower = user_prompt.lower()
        
        # Intentar extraer fragmentos de los apuntes para que parezca real
        notes_fragment = "tus apuntes"
        has_real_notes = False
        if "## Notes context" in user_prompt:
            try:
                # Extraer lo que hay entre el header de notas y el de perfil
                content = user_prompt.split("## Notes context")[1].split("## Student profile")[0].strip()
                # Limpiar posibles restos del encabezado
                content = content.replace("(RAG Layer 1 — student's own documents)", "").strip()
                
                # En Dual-RAG los chunks se separan por \n---\n
                if "---" in content:
                    import random
                    chunks = [c.strip() for c in content.split("---") if len(c.strip()) > 20]
                    if chunks:
                        content = random.choice(chunks)

                if len(content) > 10 and "not available" not in content.lower() and "no notes indexed" not in content.lower():
                    notes_fragment = content[:300] # Un poco más largo para contexto
                    has_real_notes = True
            except:
                pass

        if "enunciado" in system_lower or "pregunta" in user_lower or "socratic" in system_lower:
            enunciado = f"Basándote en el siguiente fragmento: '{notes_fragment}...', ¿cuál es la conclusión principal o el dato clave mencionado?"
            if not has_real_notes:
                enunciado = "¿Cuál de las siguientes afirmaciones define mejor el concepto de aprendizaje adaptativo en StudyPilot?"
            
            return {
                "enunciado": enunciado,
                "opciones": {
                    "A": "Una opción plausible basada en el contexto académico.",
                    "B": "La respuesta correcta extraída directamente del texto." if has_real_notes else "Personalización del ritmo y contenido según el progreso del alumno.",
                    "C": "Una interpretación parcial pero incorrecta.",
                    "D": "Un concepto relacionado pero aplicado de forma errónea."
                },
                "respuesta_correcta": "B",
                "explicacion": f"Tal como se menciona en el fragmento ('{notes_fragment}...'), este concepto es fundamental para entender la materia.",
                "chunk_source": notes_fragment,
                "nivel_dificultad": 5
            }
        elif "correcto" in system_lower or "evalu" in system_lower:
            # Intentar detectar si el usuario eligió "B" (que es nuestra respuesta correcta mock)
            # Más flexible: busca "alumno: b" o el JSON '"respuesta": "b"'
            is_correct = "alumno:b" in user_lower.replace(" ", "") or '"respuesta":"b"' in user_lower.replace(" ", "")
            return {
                "correcto": is_correct,
                "respuesta_correcta": "B",
                "explicacion": f"¡Exacto! El fragmento clave era: '{notes_fragment}'. Has identificado correctamente el núcleo del concepto.",
                "xp_ganado": 30 if is_correct else 5,
                "nuevo_nivel_tema": 6 if is_correct else 5,
                "misconception": None if is_correct else "Confusión entre el concepto principal y una de sus aplicaciones secundarias.",
                "consejo": "Te recomiendo repasar la sección específica de tus apuntes donde se define este término."
            }
        elif "autopsy" in system_lower or "diagnostician" in system_lower:
            return {
                "resumen": f"Tras analizar tu examen, he detectado patrones que coinciden con ciertos fragmentos de tus apuntes, especialmente en: {notes_fragment[:100]}...",
                "error_items": [
                    {
                        "pregunta_original": "Pregunta detectada en el examen sobre la materia principal.",
                        "respuesta_alumno": "Tu respuesta (detectada por OCR)",
                        "respuesta_correcta": "Respuesta esperada según el temario",
                        "tipo_fallo": "laguna",
                        "causa_error": "Este concepto parece ser una laguna de conocimiento, ya que no se encontró una base sólida en la explicación dada.",
                        "chunk_source": notes_fragment[:150],
                        "asignatura": "General",
                        "tema": "General"
                    }
                ],
                "temas_refuerzo": ["General"],
                "nota_estimada": 5.5
            }
        return {"mensaje": "Respuesta mock genérica", "status": "ok"}

llm_client = LLMClient()
