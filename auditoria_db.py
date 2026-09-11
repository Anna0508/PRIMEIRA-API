from fastapi import Request

from database import SessionLocal
from models import EventoAuditoria


def obter_ip_cliente(request: Request):
    return request.client.host if request.client else "desconhecido"
def registrar_auditoria(usuario: str, acao: str, resultado: str, request: Request, alvo: str = None):
    db = SessionLocal()
    try:
        evento = EventoAuditoria(
            usuario=usuario,
            acao=acao,
            alvo=alvo,
            ip_origem=obter_ip_cliente(request),
            resultado=resultado,

        )
        db.add(evento)
        db.commit()
    finally:
        db.close()

