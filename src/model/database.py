# Conexão com o banco de dados
import urllib.parse as u
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:pedrosallorenzo2301@localhost:3306/bd_ps_bd2"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


def get_session():
    # para usar nas rotas
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
