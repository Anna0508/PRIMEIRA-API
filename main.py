from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional

from config import logger
from database import USUARIOS_DB, hasher
from auth import verificar_senha, criar_token, obter_usuario_atual

app = FastAPI()

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = USUARIOS_DB.get(form_data.username)
    headers = {"WWW-Authenticate": "Bearer"}
    
    if not usuario or usuario.get("active", True) is False:
        logger.warning(f"Tentativa de login rejeitada para conta desativada: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sua conta foi desativada pelo administrador"
        )
        
    if not verificar_senha(form_data.password, usuario["password"]):
        logger.warning(f"Falha de login: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers=headers
        )
        
    token_real = criar_token(data={"sub": form_data.username})
    logger.info(f"Usuário logado com sucesso: {form_data.username}")
    return {"access_token": token_real, "token_type": "bearer"}


@app.get("/users/{user_id}")
async def acessar_painel_admin(usuario_atual: dict = Depends(obter_usuario_atual)):
    if usuario_atual.get("role") != "admin":
        logger.error(f"Acesso negado para {usuario_atual.get('username')} no painel admin.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui acesso."
        )
        
    logger.info(f"Administrador {usuario_atual.get('username')} acessou o painel")
    return {"status": "Bem-vindo ao painel admin."}


class UsuarioCriar(BaseModel):
    nome: str
    email: EmailStr
    password: str
    role: str


class UsuarioEditar(BaseModel):
    nome: Optional[str] = None
    role: Optional[str] = None


@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def criar_usuario(dados: UsuarioCriar, usuario_atual: dict = Depends(obter_usuario_atual)):
    quem = usuario_atual.get("name", "Admin")
    
    if usuario_atual.get("role") != "admin":
        logger.error(f"QUEM: {quem}, AÇÃO: CRIAR_USUARIO, EM QUEM: {dados.email}, STATUS: FALHA (Papel inválido)")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não possui acesso.")
        
  
    if dados.role not in ["admin", "user"]:
        logger.error(f"QUEM: {quem}, AÇÃO: CRIAR_USUARIO, EM QUEM: {dados.email}, STATUS: FALHA (Papel inválido)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Papel inválido. Use 'admin' ou 'user'"
        )
        
  
    if dados.email in USUARIOS_DB:
        logger.error(f"QUEM: {quem}, AÇÃO: CRIAR_USUARIO, EM QUEM: {dados.email}, STATUS: FALHA (E-mail já cadastrado)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")
        
  
    USUARIOS_DB.update({
        dados.email: {
            "name": dados.nome,
            "password": hasher.hash(dados.password),
            "role": dados.role,
            "active": True
        }
    })
    
    logger.info(f"QUEM: {quem}, AÇÃO: CRIAR_USUARIO, EM QUEM: {dados.email}, STATUS: SUCESSO")
    return {"mensagem": f"Usuário {dados.email} criado com sucesso."}

                     
                     


        
  
                     


   
              

                