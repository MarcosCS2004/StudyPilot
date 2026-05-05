# 🚀 StudyPilot — Tu Tutor Adaptativo con IA Generativa

StudyPilot es un SaaS de vanguardia diseñado para transformar la manera en que los estudiantes universitarios interactúan con su material de estudio. Utilizando una arquitectura de **Dual RAG**, algoritmos de repetición espaciada (**SM-2**) y la potencia de **Azure OpenAI**, StudyPilot genera cuestionarios personalizados, flashcards y diagnósticos de exámenes basados exclusivamente en los apuntes del usuario.

---

## ✨ Características Principales

*   **🧠 Motor de Aprendizaje Adaptativo:** Implementación real del algoritmo **SM-2** (SuperMemo) para programar repasos óptimos según el nivel de retención del alumno.
*   **🔍 Dual RAG (Retrieval-Augmented Generation):** Combina el conocimiento de tus documentos (Qdrant) con tu historial personal de errores (Postgres) para generar preguntas que atacan tus puntos débiles.
*   **📸 Autopsia de Exámenes:** Sube una foto de tu examen corregido y la IA diagnosticará el tipo de fallo (laguna de conocimiento, confusión de conceptos o error parcial).
*   **🎓 Técnica Feynman:** Explica un concepto con tus propias palabras y recibe feedback basado en la profundidad de tu comprensión.
*   **📊 Gamificación:** Sistema de experiencia (XP), niveles por tema y rachas de estudio para mantener la motivación.

---

## 🛠️ Stack Tecnológico

*   **Backend:** FastAPI (Python 3.13) + SQLAlchemy
*   **Frontend:** Next.js 14 + Tailwind CSS + Lucide Icons
*   **IA:** Azure OpenAI (GPT-4o) + Azure Document Intelligence
*   **Bases de Datos:** PostgreSQL (o SQLite para dev) + Qdrant (Vector DB)
*   **Caché:** Redis (para sesiones de estudio)

---

## 🚀 Puesta en Marcha

### 1. Requisitos Previos
*   Python 3.11+
*   Node.js 18+
*   Cuenta de Azure (opcional para modo local)

### 2. Configuración del Backend
```bash
cd backend
# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus claves de Azure/Qdrant

# Inicializar Base de Datos
python init_db.py

# Arrancar servidor
python main.py
```

### 3. Configuración del Frontend
```bash
cd frontend
npm install
npm run dev
```
Accede a `http://localhost:3000` para empezar.

---

## 🧪 Modo de Prueba (Mock Mode)
Si no dispones de una clave de Azure OpenAI en este momento, el sistema detectará automáticamente la falta de credenciales y entrará en **MOCK MODE**. 
*   Podrás navegar por toda la interfaz.
*   Recibirás preguntas de prueba predefinidas.
*   El sistema de XP y base de datos funcionará normalmente.

---

## 👥 Equipo de Desarrollo
*   **Marcos:** Backend & Data Models
*   **Ethan:** IA & RAG Services
*   **Oscar:** Frontend & UX Design

---

## 📄 Licencia
Este proyecto es parte del módulo de IA Generativa. Uso académico.
