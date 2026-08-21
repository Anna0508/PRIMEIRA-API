import os
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()
hasher = PasswordHash.recommended()

def obter_usuarios():
    return {
        "admin@email.com": {
            "nome": "admin",
            "password": hasher.hash("admin7890"),
            "role": "admin",
            "active": True
        },
        "user@email.com": {
            "nome": "user",
            "password": hasher.hash("user1234"),
            "role": "user",
            "active": True
        }
    }

USUARIOS_DB = obter_usuarios()


