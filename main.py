from config import logger, MAX_TENTATIVAS_LOGIN

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta



from database import SessionLocal, Usuario
from auth import verificar_senha, criar_token, obter_usuario_atual

DELAYS_SEGUNDOS = [2, 10, 60, 300]

TENTATIVAS_LOGIN: dict[str, dict] = {}


def calcular_delay(tentativas):
    indice = min(tentativas, MAX_TENTATIVAS_LOGIN, len(DELAYS_SEGUNDOS)) -1
    return DELAYS_SEGUNDOS[indice]


def registrar_tentativa_falha(username, info_anterior):
    if info_anterior:
        tentativas_atual = info_anterior["tentativas"] + 1
    else:
        tentativas_atual = 1
    TENTATIVAS_LOGIN[username] = {
        "tentativas": tentativas_atual,
        "proxima_tentativa_permitida": datetime.now(timezone.utc)
        + timedelta(seconds=calcular_delay(tentativas_atual)),
    }


hasher = PasswordHash.recommended()

app = FastAPI()


class UsuarioCriar(BaseModel):
    name: str
    email: str
    password: str
    role: str


class UsuarioEditar(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    active: Optional[bool] = None


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    info_tentativas = TENTATIVAS_LOGIN.get(form_data.username)

    if info_tentativas:
        if datetime.now(timezone.utc) < info_tentativas["proxima_tentativa_permitida"]:
            delay = calcular_delay(info_tentativas["tentativas"])
            raise HTTPException(
                status_code=429,
                detail=f"Excesso de tentativas de login. Tente novamente em {delay} segundos.",
            )

    session = SessionLocal()
    try:
        usuario = session.query(Usuario).filter(Usuario.email == form_data.username).first()
        if not usuario or not usuario.active or not verificar_senha(form_data.password, usuario.password):
            registrar_tentativa_falha(form_data.username, info_tentativas)
            raise HTTPException(status_code=401, detail="Credenciais invalidas")

        token = criar_token({"sub": usuario.email, "role": usuario.role})
        TENTATIVAS_LOGIN.pop(form_data.username, None)
        return {"access_token": token, "token_type": "bearer"}
    finally:
        session.close()

@app.get("/usuarios")
def listar_usuarios(
    role: str = None, 
    active: bool = None,
    usuario_logado: Usuario = Depends(obter_usuario_atual),
):
    if usuario_logado.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado.")

    session = SessionLocal()
    try:
        query = session.query(Usuario)
        if role is not None:
            query = query.filter(Usuario.role == role)
            if active is not None:
                query = query.filter(Usuario.active == active)
            usuarios = query.all()

            resultado = []
            for usuario in usuarios:
                resultado.append({
                    "id": usuario.id,
                    "email": usuario.email,
                    "name": usuario.name,
                    "role": usuario.role,
                    "active": usuario.active,
                    "create_at": usuario.create_at,
                    "update_at": usuario.update_at,
                })
                return resultado
    except Exception as e:
        logger.error(f"Erro ao listar usuarios: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
    finally:
        session.close()
    
@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    dados: UsuarioCriar, usuario_atual: dict = Depends(obter_usuario_atual)
):
    quem = usuario_atual.name 
    if usuario_atual.role != "admin":
        raise HTTPException(status_code=403, detail="acesso negado.")

    session = SessionLocal()
    try:
        usuario_existente = session.query(Usuario).filter(Usuario.email == dados.email).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")

        novo_usuario = Usuario(
            email=dados.email,
            name=dados.name,
            password=hasher.hash(dados.password),
            role=dados.role,
            active=True,
        )

        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)

        logger.info(
            f"Novo usuario criado: {dados.email} - {dados.name} - {dados.role}",
            extra={"user": quem},
        )
        return {"mensagem": "Usuario criado com sucesso!", "usuario_id": novo_usuario.id}
    finally:
        session.close()


@app.put("/usuarios/editar")
async def editar_usuario(
    email_alvo: str,
    dados: UsuarioEditar,
    usuario_atual: dict = Depends(obter_usuario_atual),
):
    quem = usuario_atual.name
    if usuario_atual.role != "admin":
        raise HTTPException(status_code=403, detail="acesso negado")

    session = SessionLocal()
    try:
        usuario = session.query(Usuario).filter(Usuario.email == email_alvo).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario não encontrado")

        if dados.name is not None:
            usuario.name = dados.name
        if dados.role is not None:
            usuario.role = dados.role
        if dados.active is not None:
            usuario.active = dados.active

        session.commit()
        logger.info(
            f"Usuario editado: {email_alvo} - dados: {dados.model_dump()}",
            extra={"user": quem},

        )
        return {"mensagem": "Usuario editado com sucesso!"}
    finally:
        session.close()
