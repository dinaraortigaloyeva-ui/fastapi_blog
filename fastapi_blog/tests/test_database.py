
from unittest.mock import Mock

from app import database


def test_get_db_yields_session_and_closes_it(monkeypatch):
    fake_db = Mock()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake_db)

    generator = database.get_db()

    db = next(generator)
    assert db is fake_db

    try:
        next(generator)
    except StopIteration:
        pass

    fake_db.close.assert_called_once()


def test_get_db_closes_session_after_error(monkeypatch):
    fake_db = Mock()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake_db)

    generator = database.get_db()
    next(generator)

    try:
        generator.throw(RuntimeError("Test xatosi"))
    except RuntimeError as exc:
        assert str(exc) == "Test xatosi"

    fake_db.close.assert_called_once()
