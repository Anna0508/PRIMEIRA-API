import os
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()
hasher = PasswordHash.recommended()

USUARIOS_DB = {
     "admin@email.com": {
         "nome":"admin",
         "password": hasher.hash("admin7890"),
         "role": "admin",
         "active": True


     },
     "user@email.com": {
         "nome":"user",
         "password": hasher.hash("user1234"),
         "role": "user",
         "active": True
        
     }
}
