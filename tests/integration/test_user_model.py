# tests/integration/test_user_model.py
"""Integration tests for the User model (the target of Calculation.user_id)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import User


def test_create_user(db_session):
    user = User(username="carol", email="carol@example.com")
    db_session.add(user)
    db_session.commit()
    assert db_session.get(User, user.id).email == "carol@example.com"
    assert user.calculations == []


@pytest.mark.parametrize("field", ["username", "email"])
def test_username_and_email_are_unique(db_session, field):
    db_session.add(User(username="dave", email="dave@example.com"))
    db_session.commit()
    dup = {"username": "other", "email": "other@example.com"}
    dup[field] = {"username": "dave", "email": "dave@example.com"}[field]
    db_session.add(User(**dup))
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()
