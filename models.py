from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from database import Base


class EventoAuditoria(Base):
    __tablename__ = "evento_auditoria"
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(255), nullable=False)
    acao = Column(String(50), nullable=False)
    alvo = Column(String(255), nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now())
    ip_origem = Column(String(45), nullable=True)
    resultado = Column(String(20), nullable=False)