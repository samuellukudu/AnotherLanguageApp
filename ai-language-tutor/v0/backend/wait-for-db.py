import time
import psycopg2
import os
from db_manager.db_setup import setup_database

def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB", "linguaai"),
                user=os.getenv("POSTGRES_USER", "linguaai_user"),
                password=os.getenv("POSTGRES_PASSWORD", "LinguaAI1008"),
                host=os.getenv("DB_HOST", "db"),  # Changed default to 'db'
                port=os.getenv("DB_PORT", "5432")
            )
            conn.close()
            print("Database is ready!")
            # Initialize database tables
            setup_database()
            break
        except psycopg2.OperationalError:
            print("Waiting for database...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_db()
