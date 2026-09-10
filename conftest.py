import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
import main
from database import Base, Usuario
from auth import hasher

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def banco_de_teste():
    engine_teste = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SessionTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine_teste)

    database.SessionLocal = SessionTeste
    main.SessionLocal = SessionTeste

    Base.metadata.create_all(bind=engine_teste)

    session = SessionTeste()
    try:  
        session.add(Usuario(
            email="admin@email.com",
            name="Admin",
            password=hasher.hash("admin7890"),
            role="admin",
            active=True,
        ))
        session.commit()
    finally:
        session.close()

    yield

    Base.metadata.drop_all(bind=engine_teste)
    engine_teste.dispose()
     

