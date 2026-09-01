import logging
import pytest

from config import configurar_auditoria, DefaultUserFilter


@pytest.fixture(autouse=True)
def resetar_logging():
    root = logging.getLogger()
    filtros_originais = root.filters[:]

    logger_uvicorn_error = logging.getLogger("uvicorn.error")
    logger_uvicorn_access = logging.getLogger("uvicorn.access")


    propagate_error_original = logger_uvicorn_error
    propagate_access_original =logger_uvicorn_access

    yield

    root.filters = filtros_originais
    logging.getLogger("uvicorn.error").propagate = propagate_error_original
    logging.getLogger("uvicorn.access").propagate = propagate_access_original


def test_log_sem_extra_user_nao_quebra():
        configurar_auditoria()
        logger_teste = logging.getLogger("teste_sem_user")

        try:
            logger_teste.info("mensagem sem campo user")
        except Exception as e:
            pytest.fail(f"log sem 'user' quebrou o sistema:{e}")


def test_default_user_filter_preencha_valor_padrao():
        filtro = DefaultUserFilter()
        record = logging.LogRecord(
            name="teste",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="mensagem qualquer",
            args=None,
            exc_info=None,
        )

        resultado = filtro.filter(record)

        assert resultado is True
        assert record.user == "sistema"


def test_default_user_filter_preserva_user_existente():
        filtro = DefaultUserFilter()
        record = logging.LogRecord(
            name="teste",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="mensagem qualquer",
            args=None,
            exc_info=None,
        )
        record.user = "usuario@email.com"

        filtro.filter(record)

        assert record.user == "usuario@email.com"

def test_uvicorn_loggers_nao_propagam():
        configurar_auditoria()

        assert logging.getLogger("uvicorn.error").propagate is False
        assert logging.getLogger("uvicorn.access").propagate is False
