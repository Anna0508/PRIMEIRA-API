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
    email_alvo:str
    nome: Optional[str] = None
    role: Optional[str] = None

class UsuarioDesativar(BaseModel):
    email_alvo:str    


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

@app.get("/usuarios")
async def listar_usuarios(usuario_atual: dict = Depends(obter_usuario_atual)):
    quem_pediu = usuario_atual.get("nome", "Desconhecido")

    if usuario_atual.get("role") != "admin":
        logger.error(f"FALHA AÇÃO: LISTAR_USUARIOS QUEM:{quem_pediu} STATUS:Bloqueado (não é admin)")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem listar usuarioa"
        )  
    return USUARIOS_DB
  
@app.put("/usuarios/editar")
async def editar_usuario(dados: UsuarioEditar, usuario_atual: dict = Depends(obter_usuario_atual)):
    if usuario_atual.get('role') != "admin":
        logger.warning(f"ACESSO NEGADO: uuario comum tentou acessar a rota")
        raise HTTPException(status_code=403, detail= "Acesso negado. Apena administradores podem desativar") 

    email_alvo = dados.email_alvo

    if email_alvo not in USUARIOS_DB:
        logger.warning(f"Tetantiva de edição falhou: o usuario{email_alvo}, não existe no banco")
        raise HTTPException(status_code=404, detail="usuario não encontrado")
 

    dados_antigos = USUARIOS_DB[email_alvo].copy()

    if dados.nome is not None:
        USUARIOS_DB[email_alvo]["nome"] = dados.nome
    if dados.role in ["admin", "user"] :
        USUARIOS_DB[email_alvo]["role"] = dados.role

    logger.info(
        f"QUEM:({email_alvo}), AÇÃO: EDITAR_USUARIO,"
        f"DADOS_ANTIGOS: (nome={dados_antigos.get('nome')}, role={dados_antigos.get('role')}),"
        f"NOVOS_DADOS: (nome-{USUARIOS_DB[email_alvo]['nome']}, role ={USUARIOS_DB[email_alvo]['role']})"

    )    

    return{"mensagem": "Dados atualizados"}

@app.patch("/usuarios/desativar")
async def desativar_usuario(dados: UsuarioDesativar,usuario_atual: dict = Depends(obter_usuario_atual)):

    if usuario_atual.get("role") != "admin":
        logger.warning(f"ACESSO NEGADO: usuario comum tentou acessar")
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem desativar usuarios")
    
    email_alvo = dados.email_alvo

    if email_alvo not in USUARIOS_DB:
        logger.warning(f"Tentativa de desativação falhou: O usuário {email_alvo} não existe.")
        raise HTTPException(status_code=404, detail="Usuário não encontrado no banco de dados.")


    USUARIOS_DB[email_alvo]["active"] = False

    logger.info(f"QUEM: ({email_alvo}), AÇÃO DESATIVAR_CONTA, STATUS: SUCESSO" )

    return{"mensagem": "Usuario desativado com sucesso!"}






        
                     
                     



                     
                     


        
  
                     


   
              

                