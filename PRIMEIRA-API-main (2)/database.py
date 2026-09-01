from pwdlib import PasswordHash

hasher = PasswordHash.recommended()

USUARIOS_DB = {
    "admin@email.com": {
        "name": "admin",
        "password": hasher.hash("admin7890"),
        "role": "admin",
        "active": True,
    },
    "user@email.com": {
        "name": "user",
        "password": hasher.hash("user1234"),
        "role": "user",
        "active": True,
    },
}


def obter_usuarios():
    return USUARIOS_DB
