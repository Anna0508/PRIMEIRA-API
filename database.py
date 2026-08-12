from pwdlib import PasswordHash
hasher = PasswordHash.recommended()

USUARIOS_DB = {
     "admin@email.com": {
         "password": hasher.hash("admin7890"),
         "role": "admin",

     },
     "user@email.com": {
         "password": hasher.hash("user1234"),
         "role": "user",
        
     }
}