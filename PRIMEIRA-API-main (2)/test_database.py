import os
from fastapi.testclient import TestClient
from main import app
from database import USUARIOS_DB

client = TestClient(app)

def test_usuarios_seed_usam_chave_name():
    for email, dados in USUARIOS_DB.items():
        assert "name" in dados, f"Usuario {email} não tem a chave 'name'"
        assert "nome" not in dados, f"usuario {email} ainda usa a chave 'nome' antiga"


def test_login_admin_retorna_name_correto_no_get_usuarios():
    login_admin = client.post(
        "/token",
        data={"username": os.getenv("ADMIN_EMAIL"), "password": os.getenv("ADMIN_SENHA")},

    )
    assert login_admin.status_code == 200
    token_admin = login_admin.json()["access_token"]

    resposta = client.get(
        "/usuarios",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert resposta.status_code == 200

    usuarios = resposta.json()
    email_admin = os.getenv("ADMIN_EMAIL")

    assert usuarios[email_admin]["name"] == "admin"
        