"""Shared fixtures — pytest auto-discovers this for every test in tests/."""
import pytest

from data.static_data.seed_data import seed
import agents.material.database_data_access as dda


@pytest.fixture
def seeded_db(tmp_path, monkeypatch):
    """A throwaway SQLite DB seeded with the dummy data, isolated per test."""
    db_path = tmp_path / "plant.db"
    seed(str(db_path))
    monkeypatch.setattr(dda, "DB_PATH", str(db_path))   # redirect reads to the temp DB
    return db_path
