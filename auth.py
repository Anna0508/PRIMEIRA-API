from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer 
from pwdlib import PasswordHash
from database import USUARIOS_DB
from config import logger

SECRET_KEY = "CHAVE_SEGURANÇA"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTE = 30

pwd_context = PasswordHash.recommended()
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def verificar_senha(plain_password, hashed_password ):
        return pwd_context.verify(plain_password, hashed_password)

def criar_token(data:dict):
        dados_copia = data.copy()
        tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
        dados_copia.update({"exp": tempo_expiracao})

        token_jwt = jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)
        return token_jwt

def obter_usuario_atual(token: str = Depends(oauth2_scheme)):
        try:
                payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
                email: str = payload.get("sub")

                if email is None:
                        raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="token invalido",
                        )
                usuario = USUARIOS_DB.get(email)
                if not usuario:
                        raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="token invalido"
                        )
                
                return usuario 
        
        except jwt.PyJWTError:
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="token invalido",
                )
        

                
                

        
    
    
        

   


             
    
