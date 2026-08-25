from config import logger

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from pwdlib import PasswordHash

from database import USUARIOS_DB
from auth import verificar_senha, criar_token, obter_usuario_atual

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
    usuario = USUARIOS_DB.get(form_data.username)
    headers = {"WWW-Authenticate": "Bearer"}

    if not usuario or not usuario.get("active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail ou senha incorretos.",
        )

    if not verificar_senha(form_data.password, usuario["password"]):
        logger.warning(
            f"Falha de login: {form_data.username}", extra={"user": "Sistema"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail ou senha incorretos.",
            headers=headers,
        )

    token_real = criar_token(dados={"sub": form_data.username})
    logger.info(
        f"Usuário logado com sucesso: {form_data.username}",
        extra={"user": usuario.get("name")},
    )
    return {"access_token": token_real, "token_type": "bearer"}


@app.get("/usuarios")
def listar_usuarios(usuario_atual: dict = Depends(obter_usuario_atual)):
    if usuario_atual.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado.")

    usuarios_seguros = {
        email: {
            chave: valor for chave, valor in dados_user.items()
            if chave != "password"
        }
        for email, dados_user in USUARIOS_DB.items()
    }
    return usuarios_seguros


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
