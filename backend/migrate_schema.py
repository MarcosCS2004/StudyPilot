from app.db.session import engine
from sqlalchemy import text

def migrate():
    print("Migrando base de datos...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE ExamAutopsies ADD COLUMN ExamImageUrl VARCHAR(255)"))
            conn.commit()
            print("Columna ExamImageUrl añadida a ExamAutopsies.")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("La columna ya existe.")
            else:
                print(f"Error: {e}")

if __name__ == "__main__":
    migrate()
