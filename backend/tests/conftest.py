import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app.main import app

DB_URL = os.getenv("DATABASE_URL", "")


def _db_disponible() -> bool:
    if not DB_URL:
        return False
    try:
        with create_engine(DB_URL).connect() as c:
            c.execute(text("select 1 from usuario limit 1"))
        return True
    except Exception:
        return False


requiere_db = pytest.mark.skipif(not _db_disponible(), reason="Sin base de datos de pruebas (DATABASE_URL)")


@pytest.fixture
def cliente() -> TestClient:
    return TestClient(app)
