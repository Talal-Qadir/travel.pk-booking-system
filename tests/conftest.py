import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB_PATH = Path(tempfile.mkdtemp(prefix="travelpk-tests-")) / "travelpk.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from app.db.database import Base, engine, init_db
from app.db.seed import seed_database
from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def partner_headers():
    return {"Authorization": "partner-admin"}


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    init_db()
    seed_database()
    yield
    Base.metadata.drop_all(bind=engine)
    init_db()
    seed_database()
