from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import USUARIOS_DB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def obter_usuario_atual(token: str = Depends(oauth2_scheme)):
    usuario = USUARIOS_DB.get(token)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inalido"
        )
    return usuario

def verificar_permissao_admin(usuario: dict = Depends(obter_usuario_atual)):
    if usuario["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão de administardor necessária"

        )
    return True