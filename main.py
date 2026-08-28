from config import logger, MAX_TENTATIVAS_LOGIN

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
import time


from database import USUARIOS_DB
from auth import verificar_senha, criar_token, obter_usuario_atual

DELAYS_SEGUNDOS = [2, 10, 60, 300]

TENTATIVAS_LOGIN: dict[str, dict] = {}

def calcular_delay(tentativas):
    indice = min(tentativas, MAX_TENTATIVAS_LOGIN) - 1
    indice = min(indice, len(DELAYS_SEGUNDOS)) - 1
    return DELAYS_SEGUNDOS[indice]


def registrar_tentativa_falha(username, info_anterior):
    if info_anterior:
        tentativas_atual = info_anterior["tentativas"] + 1
    else:
        tentativas_atual = 1
    TENTATIVAS_LOGIN[username] = {
        "tentativas": tentativas_atual,
        "proxima_tentativa_permitida": datetime.now(timezone.utc)
        +timedelta(seconds=calcular_delay(tentativas_atual)),
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
        espera = (
            info_tentativas["proxima_tentativa_permitida"] - datetime.now(timezone.utc)
        ).total_seconds()
        if espera > 0:
            time.sleep(espera)


    usuario = USUARIOS_DB.get(form_data.username)
    headers = {"WWW-Authenticate": "Bearer"}

    if not usuario or not usuario.get("active"):
        registrar_tentativa_falha(form_data.username, info_tentativas)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    if not verificar_senha(form_data.password, usuario["password"]):
        logger.warning(
            f"Falha de login: {form_data.username}", extra={"user": "Sistema"}
        )
        registrar_tentativa_falha(form_data.username, info_tentativas)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers=headers,
        )

    TENTATIVAS_LOGIN.pop(form_data.username, None)
    token_real = criar_token(dados={"sub": form_data.username})
    logger.info(
        f"Usuário logado com sucesso: {form_data.username}",
        extra={"user": usuario.get("name")},
    )
    return {"access_token": token_real, "token_type": "bearer"}


@app.get("/usuarios")
def listar_usuarios(
    usuario_atual: dict = Depends(obter_usuario_atual),
    perfil: Optional[str] = None,
    status_usuario: Optional[str] = Query(None, alias="status"),
):
    if usuario_atual.get("role") != "admin":
        raise HTTPException(status_code=403, detail="acesso negado")
    if status_usuario is not None  and status_usuario not in ("ativo", "inativo"):
        raise HTTPException(
            status_code=422, detail="status deve ser 'ativo' ou 'inativo'."
        )
    ativo_filtro = None
    if status_usuario == 'ativo':
        ativo_filtro = True
    elif status_usuario ==  'inativo':
        ativo_filtro = False

    usuarios_seguro = {}
    for email, dados_user in USUARIOS_DB.items():
        if perfil is not None and dados_user.get("role") != perfil:
            continue
        if ativo_filtro is not None and dados_user.get("active") != ativo_filtro:
            continue

        usuarios_seguro[email] = {
            chave: valor for chave, valor in dados_user.items()
            if chave !=" password"
        }

        return usuarios_seguro


@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    dados: UsuarioCriar, usuario_atual: dict = Depends(obter_usuario_atual)
):
    
    quem = usuario_atual.get("name", "Admin")
    if usuario_atual.get("role") != "admin":
        logger.error("FALHA: Sem permissão", extra={"user": quem})
        raise HTTPException(status_code=403, detail="Você não possui acesso.")

    if dados.email in USUARIOS_DB:
        logger.error("FALHA: E-mail cadastrado", extra={"user": quem})
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    USUARIOS_DB[dados.email] = {
        "name": dados.name,
        "password": hasher.hash(dados.password),
        "role": dados.role,
        "active": True,
    }

    logger.info(
        f"QUEM: {quem}, AÇÃO: CRIAR_USUARIO,"
        f"EM QUEM: {dados.email}, STATUS: SUCESSO",
        extra={"user": quem},
    )
    return {"mensagem": f"Usuário {dados.email} criado com sucesso."}


@app.put("/usuarios/editar")
async def editar_usuario(
    email_alvo: str,
    dados: UsuarioEditar,
    usuario_atual: dict = Depends(obter_usuario_atual),
):
    quem = usuario_atual.get("name", "Admin")

    if usuario_atual.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado.")

    if email_alvo not in USUARIOS_DB:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    dados_antigos = USUARIOS_DB[email_alvo].copy()

    if dados.name is not None:
        USUARIOS_DB[email_alvo]["name"] = dados.name
    if dados.role is not None:
        USUARIOS_DB[email_alvo]["role"] = dados.role
    if dados.active is not None:
        USUARIOS_DB[email_alvo]["active"] = dados.active

    logger.info(
        f"Alterou a conta de [{email_alvo}]. Antigos:"
        f"{dados_antigos.get('role')}"
        f"Novos: {USUARIOS_DB[email_alvo].get('role')}",
        extra={"user": quem},
    )
    return {"mensagem": "Cadastro atualizado com sucesso!"}