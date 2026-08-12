from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm


from config import logger
from database import USUARIOS_DB
from fastapi import Depends, HTTPException, status
from auth import obter_usuario_atual, verificar_permissao_admin


app = FastAPI(title="API segura")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = USUARIOS_DB.get(form_data.username)
    if not usuario or usuario["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário invalido",
            headers={"WWW-Authenticate": "Bearer"},

        )
    logger.info(f"Usuário logado: {form_data.username}")

    return {"access_token": form_data.username, "token_type": "bearer"}

@app.get("/admin/painel")
async def painel_admin(usuario: dict = Depends(obter_usuario_atual)):
    print(usuario)
    logger.info(f"Usuário com permissãoo de admin acessou o painel_admin")
    return {"mensaagem": "Bem-vindo ao painel de admin"}


@app.get("/users/{user_id}")
def get_user(user_id: str, usuario: dict = Depends(obter_usuario_atual)):
    logger.info(f"Usuário {usuario} acessou o endpoint /users/{user_id}")

    return {"user_id": user_id, "usuario": usuario} 

   
              

                