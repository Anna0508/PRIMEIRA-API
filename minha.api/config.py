import logging 
def configurar_auditoria():
    logging.getLogger("ouvicorn").handlers.clear()

    logging.basicConfig(
        filename="auditoria.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        encoding="utf-8"

    )
    return logging.getLogger("auditoria")

logger = configurar_auditoria()