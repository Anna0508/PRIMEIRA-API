from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from pydantic import BaseModel, EmailStr


from config import logger
from database import USUARIOS_DB
from auth import obter_usuario_atual, verificar_senha, criar_token

app= FastAPI()

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = USUARIOS_DB.get(form_data.username)

    if not usuario:
        logger.warning(f"Falha no login:{form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario ou senha incorreto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.get("active", True):
        logger.warning(f"tentativa de login rejeitada para conta desativada:{form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sua conta foi desativada pelo administrador"
        )
    if not verificar_senha(form_data.password, usuario["password"]):
        logger.warning(f"Falha de login:{form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="usuario ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_real=criar_token(data={"sub": form_data.username})
    logger.info(f"Usuario logado com sucesso:{form_data.username}")
    return{"access_token":token_real,"token_type":"bearer"}


@app.get("/ users/{user_id}")
async def acessar_painel_admin(usuario_atual: dict = Depends(obter_usuario_atual)):

    if usuario_atual.get("role") != "admin":
        logger.error(f"Acesso negado para {usuario_atual.get('username')}no painel admin.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui acesso."
        )

    logger.info(f"Administardor {usuario_atual.get('username')} acessou o painel")
    return{"status": "Bem-vindo ao painel adm", }

class UsuarioCriar(BaseModel):
    nome: str 
    email: EmailStr
    password: str
    role: str

class UsuarioEditar(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None

@app.post("/usuarios", status_code=201)
async def criar_usuario(dados: UsuarioCriar, usuario_atual: dict = Depends(obter_usuario_atual)):
    quem = usuario_atual.get("username","Admin")

    if usuario_atual.get("role") != "admin":
        logger.error(f"QUEM:{quem}, AÇÃO: CRIAR_USUARIO, EM QUEM: {dados.email}, STATUS: FALHA(Papel invállido)")
        raise HTTPException(status_code=403, detail="Você não possui acesso.")

    if dados.role not in ["admin", "user"]:
        logger.error(f"QUEM: {quem}, AÇÃO: CRIAR_USUARIO, EM QUEM:{dados.email}, STATUS: FALHA(Papel inválido)")
        raise HTTPException(status_code=400, detail="Papel inválido. use 'admin' ou 'user'")

    if dados.email in USUARIOS_DB:
        logger.error(f"QUEM: {quem}, AÇÃO:CRIAR_USUARIO, EM QUEM:{dados.email},status: FALHA 9papel inválido")
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    USUARIOS_DB[dados.email]={
        "name":dados.nome,
        "password":hasher.hash(dados.password),
        "role" : dados.role,
        "active":True
    }

    logger.info(f"QUEM:{quem}, AÇÃO: CRIAR_USUARIO, EM QUEM:{dados.email}, STATUS: SUCESSO")
    return {"mensagem": f"Usuário {dados.emai} criado com sucesso."}
                     
                     


        
  
                     


   
              

                