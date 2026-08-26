import os
import logging
from dotenv import load_dotenv

load_dotenv()


def carregar_secret_key():
    chave = os.getenv("SECRET_KEY")
    if not chave:
        raise ValueError(
            "SECRET_KEY NÃO DEFINIDA!"
            "configure a varial antes de inicar o servidor"
        )
    return chave


SECRET_KEY = carregar_secret_key()
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def configurar_auditoria():
    logging.getLogger("ouvicorn").handlers.clear()

    logging.basicConfig(
        filename="auditoria.log",
        level=logging.INFO,
        format="%(asctime)s - %(user)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    return logging.getLogger("auditoria")


logger = configurar_auditoria()
