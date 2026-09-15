# API de Usuários

API em FastAPI com autenticação (JWT), autorização por role e filtros por
query parameters, usando SQLAlchemy + MariaDB.

## Requisitos

- Python 3.14+
- Um servidor MariaDB acessível

## Instalação

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com:

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `SECRET_KEY` | sim | — | chave usada para assinar os tokens JWT |
| `DATABASE_URL` | sim | — | string de conexão do banco, ex: `mysql+pymysql://usuario:senha@host:3306/nome_do_banco` |
| `ALGORITHM` | não | `HS256` | algoritmo de assinatura do JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | não | `30` | tempo de validade do token de acesso |
| `MAX_TENTATIVAS_LOGIN` | não | `4` | número de tentativas de login antes de aplicar o maior delay |

## Como rodar

```bash
uvicorn main:app --reload
```

A API sobe em `http://127.0.0.1:8000`. Documentação interativa em
`http://127.0.0.1:8000/docs`.

## Como rodar os testes

Os testes ficam na pasta `tests/`. Rode a partir da raiz do projeto com:

```bash
python -m pytest
```

Use `python -m pytest` (e não só `pytest`), pois é o `-m` que garante que o
diretório raiz do projeto (onde ficam `main.py`, `config.py` etc.) seja
encontrado pelos imports dos testes.
