# tests/unit/test_calculation_model.py
"""Unit tests for the Calculation model's factory-backed constructor (no database)."""

import uuid

import pytest

from app.models import Calculation
from app.schemas import CalculationType


@pytest.mark.parametrize(
    "calc_type, a, b, expected_type, expected_result",
    [
        ("Add", 2, 3, "Add", 5),
        (CalculationType.SUB, 9, 4, "Sub", 5),
        ("multiply", 3, 4, "Multiply", 12),
        ("DIVIDE", 8, 2, "Divide", 4),
    ],
)
def test_create_sets_type_and_result(calc_type, a, b, expected_type, expected_result):
    calc = Calculation.create(calc_type, a, b)
    assert calc.type == expected_type
    assert calc.result == expected_result
    assert calc.user_id is None


def test_create_keeps_user_id():
    uid = uuid.uuid4()
    assert Calculation.create("Add", 1, 1, user_id=uid).user_id == uid


def test_create_unsupported_type_raises():
    with pytest.raises(ValueError):
        Calculation.create("Modulo", 1, 2)


def test_create_divide_by_zero_raises():
    with pytest.raises(ValueError):
        Calculation.create("Divide", 1, 0)


def test_compute_result_matches_stored_result():
    calc = Calculation(a=6, b=3, type="Divide")
    assert calc.compute_result() == 2
