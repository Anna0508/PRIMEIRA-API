from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordRequestForm


from config import logger
from database import USUARIOS_DB
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
async def painel_admin(usuario: dict = Depends(verificar_permissao_admin)):
    logger.info(f"Usuário com permissãoo de admin acessou o painel_admin")
    return {"mensaagem": "Bem-vindo ao painel de admin"}


@app.get("/users/{user_id}")
def get_user(user_id: str):
    user = USUARIOS_DB.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user





   
              

                