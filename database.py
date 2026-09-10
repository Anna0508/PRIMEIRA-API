from sqlalchemy import DateTime, create_engine, Column, String, Boolean, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()
print(repr(os.getenv("DATABASE_URL")))

DATABASE_URL = os.getenv("DATABASE_URL")
MARIADB_USER = os.getenv("MARIADB_USER")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD")
MARIADB_DATABASE = os.getenv("MARIADB_DATABASE")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False,index=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    create_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    update_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
from models import EventoAuditoria
Base.metadata.create_all(bind=engine)

def obter_usuarios_por_email(email):
    session = SessionLocal()
    try:
        usuarios = session.query(Usuario).filter(Usuario.email == email).first()
        return usuarios
    finally:
        session.close()

