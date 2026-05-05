"""
Algoritmo de Spaced Repetition SM-2
Basado en: https://www.supermemo.com/english/smtwo.htm
"""

class SM2Engine:
    def __init__(self):
        self.initial_ef = 2.5  # Easiness Factor
        self.min_ef = 1.3
    
    def calculate_next_interval(self, ef: float, n: int, quality: int) -> dict:
        """
        Calcula el siguiente intervalo, n y EF
        quality: 0-5 (0=complete blackout, 5=perfect response)
        Returns: {"interval": int, "ef": float, "n": int}
        """
        if quality < 3:
            # Si el alumno falló (calidad < 3), reiniciamos n y el intervalo a 1 día
            return {"interval": 1, "ef": ef, "n": 0}
        
        if n == 0:
            new_interval = 1
        elif n == 1:
            new_interval = 6
        else:
            new_interval = int(n * ef)
            
        # Fórmula clásica para el nuevo Easiness Factor
        new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(self.min_ef, new_ef)
        
        return {
            "interval": new_interval,
            "ef": new_ef,
            "n": n + 1
        }
    
    async def get_next_review_date(self, last_review_date, interval_days: int):
        """Calcula la próxima fecha de revisión sumando el intervalo"""
        from datetime import timedelta, datetime
        if last_review_date is None:
            last_review_date = datetime.utcnow()
        return last_review_date + timedelta(days=interval_days)

sm2_engine = SM2Engine()
