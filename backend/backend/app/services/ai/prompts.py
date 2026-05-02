"""
Templates de GPT-4o para preguntas y Exam Autopsy
"""

QUESTION_TEMPLATE = """
Basándote en el siguiente contexto, genera una pregunta de opción múltiple:

Contexto: {context}

Requisitos:
- Dificultad: {difficulty}
- Tema: {topic}
- 4 opciones (A, B, C, D)
- Respuesta correcta clara
"""

AUTOPSY_TEMPLATE = """
Analiza por qué el estudiante falló en estas preguntas:

Preguntas falladas: {failed_questions}
Historial de errores: {error_history}

Proporciona:
1. Conceptos clave no comprendidos
2. Áreas de mejora
3. Plan de estudio recomendado
"""
