# src/model/database.py
import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,  # porta do host (compose)
    "user": "root",
    "password": "root123",  # troque se sua senha for outra
    "database": "db_projeto_ps_bd2",  # nome do seu banco corrigido
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def ping() -> bool:
    conn = cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        return cur.fetchone() == (1,)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("Conexão bem-sucedida! ✅" if ping() else "Falha na conexão ❌")
