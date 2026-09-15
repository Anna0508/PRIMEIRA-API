import os
import logging
from dotenv import load_dotenv

load_dotenv()


def carregar_secret_key():
    chave = os.getenv("SECRET_KEY")
    if not chave:
        raise ValueError(
            "SECRET_KEY NÃO DEFINIDA!" "configure a varial antes de inicar o servidor"
        )
    return chave
def carregar_database_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL NÃO DEFINIDA! configure a variável antes de iniciar o servidor"
        )
    return url


MAX_TENTATIVAS_LOGIN = int(os.getenv("MAX_TENTATIVAS_LOGIN", 4))
SECRET_KEY = carregar_secret_key()
DATABASE_URL = carregar_database_url()
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class DefaultUserFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "user"):
            record.user = "sistema"
        return True


def configurar_auditoria():
    logging.getLogger("uvicorn.error").propagate = False
    logging.getLogger("uvicorn.access").propagate = False

    logging.basicConfig(
        filename="auditoria.log",
        level=logging.INFO,
        format="%(asctime)s - %(user)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )

    for handler in logging.getLogger().handlers:
        handler.addFilter(DefaultUserFilter())

    return logging.getLogger("auditoria")


logger = configurar_auditoria()

