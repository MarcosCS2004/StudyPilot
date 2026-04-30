"""
Algoritmo de Spaced Repetition SM-2
Basado en: https://www.supermemo.com/english/smtwo.htm
"""

class SM2Engine:
    def __init__(self):
        self.initial_ef = 2.5  # Easiness Factor
        self.min_ef = 1.3
    
    def calculate_next_interval(self, ef: float, n: int, quality: int) -> tuple:
        """
        Calcula el siguiente intervalo y EF
        quality: 0-5 (0=complete blackout, 5=perfect response)
        """
        if quality < 3:
            return 1, ef
        
        if n == 0:
            return 1, ef
        elif n == 1:
            return 3, ef
        else:
            new_interval = int(n * ef)
            new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            new_ef = max(self.min_ef, new_ef)
            return new_interval, new_ef
    
    async def get_next_review_date(self, user_id: str, topic: str):
        """Obtener próxima fecha de revisión"""
        pass
