# 🚀 StudyPilot: Estado del Proyecto y Handover Frontend-Backend

Este documento resume el estado actual de la integración entre el Frontend y el Backend, y detalla exactamente los próximos pasos necesarios para conectar la lógica real del sistema.

---

## 1. ¿Qué está 100% terminado y funcionando? ✅

La "tubería" principal de la aplicación ya está construida y conectada. Esto incluye:

*   **UI/UX (Frontend):** Las 3 pantallas principales (Dashboard, Sesión de Estudio y Autopsia de Examen) están terminadas con React, Tailwind CSS y animaciones en Framer Motion. 
*   **Gestión de Estados y Red:** React Query configurado para peticiones, caché y validaciones.
*   **Modelos de Datos Compartidos:** Los esquemas de respuesta del Backend (`pydantic` models en `backend/app/schemas/api.py`) coinciden byte a byte con los tipos de TypeScript del Frontend (`frontend/src/types/api.ts`).
*   **Backend Base (FastAPI):** El servidor está configurado, arranca sin errores usando una base de datos local temporal (SQLite), tiene CORS configurado y expone los **5 Endpoints clave** respondiendo con **datos mock funcionales (estáticos)**.
*   **Autenticación (Login):** La pantalla de login del frontend está construida y funcional. Cuenta con un sistema gestor de sesiones (Zustand) que inyecta automáticamente el token JWT en las cabeceras de todas las llamadas. El backend cuenta con un endpoint (`POST /auth/login`) que ahora mismo devuelve un token JWT simulado genérico para poder entrar y probar.

Actualmente, el sistema se puede levantar entero y es totalmente navegable.

---

## 2. ¿Qué falta por implementar? (Tareas para el Backend) 🚧

Toda la estructura base ya está en `backend/app/api/v1/`. El trabajo restante consiste exclusivamente en **entrar a cada uno de esos 5 Endpoints, borrar los datos simulados (los `MOCK_*`), y escribir la lógica real** que conecta con la IA y la Base de Datos.

### A) Módulo: Perfil y Dashboard (`profile.py`)
*   **Endpoint:** `GET /api/v1/profile/progress`
*   **Tarea:** Conectar a la base de datos PostgreSQL. Obtener el `User` (racha, XP total) y hacer un JOIN con la tabla `Performance` para devolver los temas agrupados por asignaturas con su nivel de dominio y % de acierto.

### B) Módulo: Sesión de Estudio (`study.py`)
*   **Endpoint:** `GET /api/v1/study/next-question`
*   **Tarea:** 
    1. Usar el algoritmo adaptativo (`sm2_engine.py`) para decidir qué tema le toca estudiar al alumno.
    2. Llamar al LLM (Azure/OpenAI) pidiéndole que genere una pregunta de opción múltiple con 4 opciones sobre ese tema.
*   **Endpoint:** `POST /api/v1/study/answer`
*   **Tarea:**
    1. Evaluar si la respuesta que mandó el usuario (`A, B, C, D`) es correcta.
    2. Usar el LLM para generar una explicación pedagógica sobre la respuesta.
    3. Actualizar la tabla `Performance` sumando los Puntos de Experiencia (XP) y actualizando el multiplicador SM-2.

### C) Módulo: Ingesta Documental y RAG (`documents.py`)
*   **Endpoint:** `POST /api/v1/documents/upload`
*   **Tarea:**
    1. Recibir el archivo adjunto (`.pdf`, `.docx`, `.jpg`).
    2. Extraer el texto completo usando Azure Document Intelligence (OCR).
    3. Trocear el texto (Chunking) e insertarlo vectorizado en Qdrant (Vector DB).

### D) Módulo: Autopsia de Examen (`autopsy.py`)
*   **Endpoint:** `POST /api/v1/exam-autopsy/upload`
*   **Tarea:**
    1. Usar OCR para leer el examen que sube el alumno.
    2. Identificar qué preguntas falló.
    3. **RAG:** Por cada fallo, buscar en Qdrant el fragmento exacto de los apuntes del alumno (`chunk_source`) que debía saberse para acertar.
    4. Que el LLM dictamine la causa del error ("laguna", "confusión" o "parcial") y genere un resumen general.

### E) Módulo de Autenticación (Login/Registro) 🔐
*   **Endpoint:** `POST /api/v1/auth/login` (Actualmente tiene lógica Mock)
*   **Tarea (Lo que falta realmente):**
    1. Reemplazar mi token simulado (`mock-jwt-token-12345`) en `auth.py` conectando con la Base de Datos para verificar usuarios reales y contraseñas (ej. usando Passlib).
    2. Firmar un token JWT criptográficamente seguro usando librerías como PyJWT.
    3. Asegurar los demás endpoints (Dashboard, Estudio, etc.) añadiendo una inyección de dependencias (ej. `Depends(get_current_user)`) en FastAPI para que los datos devueltos (rachas, progreso, asignaturas) se correspondan con el token recibido.

---

## 3. Notas Técnicas y Próximos Pasos 💻

1. **Variables de Entorno:** Ahora mismo `backend/app/core/config.py` tiene todo puesto de forma opcional para permitir el arranque rápido. El Backend Developer tendrá que poner sus credenciales de OpenAI, Azure, Redis y Postgres en un `.env` en la carpeta `backend/`.
2. **Dependencias:** El Backend requiere `pip install -r requirements.txt`.
3. **Frontend Local:** El Frontend está asumiendo que el backend corre en `http://localhost:8000/api/v1`.
