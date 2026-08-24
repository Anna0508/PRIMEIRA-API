from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import obter_usuarios

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def criar_token(dados: dict):
    dados_copia = dados.copy()

    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_copia.update({"exp": tempo_expiracao})

    token_jwt = jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

def obter_usuario_atual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise HTTPException(status_code=401, detail="token invalido")
            
        usuarios = obter_usuarios()
        usuario = usuarios.get(email)
        
        if usuario is None:
            raise HTTPException(status_code=401, detail="Token invalido")
            
        return usuario
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalido")









