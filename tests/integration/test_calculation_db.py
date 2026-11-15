# tests/integration/test_calculation_db.py
"""Integration tests: Calculation records against a real database."""

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Calculation, User
from app.schemas import CalculationCreate, CalculationRead


def _make_user(session, name="alice"):
    user = User(username=name, email=f"{name}@example.com")
    session.add(user)
    session.flush()
    return user


@pytest.mark.parametrize(
    "calc_type, a, b, expected",
    [("Add", 2, 3, 5), ("Sub", 10, 4, 6), ("Multiply", 6, 7, 42), ("Divide", 9, 3, 3)],
)
def test_insert_and_read_back_each_type(db_session, calc_type, a, b, expected):
    calc = Calculation.create(calc_type, a, b)
    db_session.add(calc)
    db_session.commit()

    stored = db_session.get(Calculation, calc.id)
    assert (stored.a, stored.b, stored.type, stored.result) == (a, b, calc_type, expected)
    assert stored.created_at is not None


def test_pydantic_to_database_round_trip(db_session):
    payload = CalculationCreate(a=7, b=2, type="divide")
    calc = Calculation.create(payload.type, payload.a, payload.b)
    db_session.add(calc)
    db_session.commit()

    read = CalculationRead.model_validate(db_session.get(Calculation, calc.id))
    assert read.id == calc.id
    assert (read.a, read.b, read.type.value, read.result) == (7, 2, "Divide", 3.5)


def test_calculation_linked_to_user(db_session):
    user = _make_user(db_session)
    calc = Calculation.create("Add", 1, 2, user_id=user.id)
    db_session.add(calc)
    db_session.commit()

    assert calc.user.username == "alice"
    assert [c.id for c in user.calculations] == [calc.id]


def test_invalid_user_foreign_key_rejected(db_session):
    import uuid

    db_session.add(Calculation.create("Add", 1, 2, user_id=uuid.uuid4()))
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_deleting_user_deletes_their_calculations(db_session):
    user = _make_user(db_session, "bob")
    db_session.add(Calculation.create("Add", 1, 2, user_id=user.id))
    db_session.commit()

    db_session.delete(user)
    db_session.commit()
    assert db_session.scalars(select(Calculation)).all() == []


# ------------------------------------------------------------------ error cases
def test_invalid_type_rejected_by_database(db_session):
    db_session.add(Calculation(a=1, b=2, type="Modulo", result=0))
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_divide_by_zero_rejected_by_database(db_session):
    db_session.add(Calculation(a=1, b=0, type="Divide", result=None))
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_missing_operand_rejected_by_database(db_session):
    db_session.add(Calculation(a=1, b=None, type="Add"))
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


@pytest.mark.parametrize(
    "payload",
    [
        {"a": 1, "b": 2, "type": "Modulo"},
        {"a": 1, "b": 0, "type": "Divide"},
        {"a": "x", "b": 2, "type": "Add"},
    ],
)
def test_invalid_payload_never_reaches_database(db_session, payload):
    with pytest.raises(ValidationError):
        CalculationCreate(**payload)
    assert db_session.scalars(select(Calculation)).all() == []
