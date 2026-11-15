# tests/unit/test_calculation_schemas.py
"""Unit tests for the CalculationCreate / CalculationRead Pydantic schemas."""

from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import CalculationCreate, CalculationRead, CalculationType


# ---------------------------------------------------------------- CalculationCreate
@pytest.mark.parametrize("type_str", ["Add", "Sub", "Multiply", "Divide"])
def test_create_accepts_valid_types(type_str):
    calc = CalculationCreate(a=10, b=2, type=type_str)
    assert calc.type == CalculationType(type_str)
    assert calc.a == 10 and calc.b == 2
    assert calc.user_id is None


@pytest.mark.parametrize("type_str", ["add", "ADD", " sub ", "mUlTiPlY", "divide"])
def test_create_type_is_case_insensitive(type_str):
    calc = CalculationCreate(a=1, b=1, type=type_str)
    assert calc.type.value.lower() == type_str.strip().lower()


@pytest.mark.parametrize("bad_type", ["Modulo", "", "addition", None, 7, ["Add"]])
def test_create_rejects_invalid_type(bad_type):
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, b=2, type=bad_type)


def test_create_divide_by_zero_rejected():
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationCreate(a=5, b=0, type="Divide")


def test_create_zero_numerator_and_non_divide_zero_allowed():
    assert CalculationCreate(a=0, b=5, type="Divide").a == 0
    assert CalculationCreate(a=5, b=0, type="Add").b == 0
    assert CalculationCreate(a=5, b=0, type="Multiply").b == 0


@pytest.mark.parametrize("missing", ["a", "b", "type"])
def test_create_missing_field_rejected(missing):
    data = {"a": 1, "b": 2, "type": "Add"}
    data.pop(missing)
    with pytest.raises(ValidationError):
        CalculationCreate(**data)


@pytest.mark.parametrize(
    "field, value", [("a", "abc"), ("b", "xyz"), ("a", None), ("b", [1]), ("a", float("nan")), ("b", float("inf"))]
)
def test_create_non_finite_or_non_numeric_operand_rejected(field, value):
    data = {"a": 1, "b": 2, "type": "Add", field: value}
    with pytest.raises(ValidationError):
        CalculationCreate(**data)


def test_create_user_id_must_be_uuid():
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, b=2, type="Add", user_id="not-a-uuid")
    uid = uuid4()
    assert CalculationCreate(a=1, b=2, type="Add", user_id=uid).user_id == uid


# ---------------------------------------------------------------- CalculationRead
def _row(**overrides):
    row = dict(
        id=uuid4(), a=1.0, b=2.0, type="Add", result=3.0, user_id=None,
        created_at=datetime(2026, 1, 1), password_hash="secret", email="x@y.z",
    )
    row.update(overrides)
    return SimpleNamespace(**row)


def test_read_from_orm_object():
    row = _row()
    read = CalculationRead.model_validate(row)
    assert read.id == row.id
    assert (read.a, read.b, read.result) == (1.0, 2.0, 3.0)
    assert read.type == CalculationType.ADD


def test_read_does_not_expose_extra_attributes():
    dumped = CalculationRead.model_validate(_row()).model_dump()
    assert set(dumped) == {"id", "a", "b", "type", "result", "user_id", "created_at"}
    assert "password_hash" not in dumped and "email" not in dumped


def test_read_rejects_invalid_type():
    with pytest.raises(ValidationError):
        CalculationRead.model_validate(_row(type="Modulo"))
