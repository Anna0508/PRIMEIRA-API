from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm


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
            headers={"WWWA-Authenticate": "Bearer"},
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

   
              

                