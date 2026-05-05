from app.db.session import engine
from sqlalchemy import text

def clear_autopsies():
    print("Borrando historial de autopsias...")
    with engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM AutopsyErrors"))
            conn.execute(text("DELETE FROM ExamAutopsies"))
            conn.commit()
            print("Historial borrado con éxito.")
        except Exception as e:
            print(f"Error al borrar: {e}")

if __name__ == "__main__":
    clear_autopsies()
