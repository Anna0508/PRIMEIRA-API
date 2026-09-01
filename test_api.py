from fastapi.testclient import TestClient
from main import app

import main 
import pytest

@pytest.fixture(autouse=True)
def limpar_tentativas_login():
    main.TENTATIVAS_LOGIN.clear()
    yield

client = TestClient(app)

ADMIN_EMAIL = "admin@email.com"
ADMIN_SENHA = "admin7890"


def test_admin_faz_login_e_recebe_token():
    response = client.post(
        "/token",
        data={"username": ADMIN_EMAIL, "password": ADMIN_SENHA},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["access_token"] != ""


def test_senha_errada_e_rejeitada():
    response = client.post(
        "/token",
        data={"username": ADMIN_EMAIL, "password": "senha_errada_qualquer"},
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()


def test_admin_cria_usuario_que_faz_login_e_usa_o_token():
    login_admin = client.post(
        "/token",
        data={"username": ADMIN_EMAIL, "password": ADMIN_SENHA},
    )
    assert login_admin.status_code == 200
    token_admin = login_admin.json()["access_token"]

    novo_email = "usuario_teste_automatizado@email.com"
    novo_senha = "senha123"

    cadastro = client.post(
        "/usuarios",
        json={
            "name": "usuario teste",
            "email": novo_email,
            "password": novo_senha,
            "role": "user",
        },
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert cadastro.status_code == 201

    login_novo_usuario = client.post(
        "/token",
        data={"username": novo_email, "password": novo_senha},
    )
    assert login_novo_usuario.status_code == 200
    token_novo_usuario = login_novo_usuario.json()["access_token"]

    resposta_protegida = client.get(
        "/usuarios",
        headers={"Authorization": f"Bearer {token_novo_usuario}"},
    )
    assert resposta_protegida.status_code == 403

def test_filtro_por_perfil():
    token_admin = client.post(

         "/token", data={"username": ADMIN_EMAIL, "password": ADMIN_SENHA}
    ).json()["access_token"]

    resposta = client.get(
        "/usuarios",
        params={"perfil": "admin"},
        headers={"Authorization": f"Bearer {token_admin}"},
    )

    assert resposta.status_code == 200
    usuarios = resposta.json()
    assert all(u["role"] == "admin" for u in usuarios.values())


def test_filtro_por_status_ativo():
    token_admin = client.post(
        "/token", data={"username": ADMIN_EMAIL, "password": ADMIN_SENHA}
    ).json()["access_token"]

    resposta = client.get(
        "/usuarios",
        params={"status": "ativo"},
        headers={"Authorization": f"Bearer {token_admin}"},
    )

    assert resposta.status_code == 200
    usuarios = resposta.json()
    assert all(u["active"] is True for u in usuarios.values())


def test_filtro_status_invalido_retorna_422():
    token_admin = client.post(
        "/token", data={"username": ADMIN_EMAIL, "password": ADMIN_SENHA}
    ).json()["access_token"]

    resposta = client.get(
        "/usuarios",
        params={"status": "banana"},
        headers={"Authorization": f"Bearer {token_admin}"},
    )

    assert resposta.status_code == 422

    

