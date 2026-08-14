from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer


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
        
  
                     


   
              

                