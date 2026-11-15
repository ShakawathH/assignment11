# tests/unit/test_calculation_factory.py
"""Unit tests: the factory picks the right operation and each operation is correct."""

import pytest

from app.operations.factory import (
    AddOperation,
    CalculationFactory,
    DivideOperation,
    MultiplyOperation,
    Operation,
    SubOperation,
)
from app.schemas.calculation import CalculationType


@pytest.mark.parametrize(
    "calc_type, expected_class",
    [
        (CalculationType.ADD, AddOperation),
        (CalculationType.SUB, SubOperation),
        (CalculationType.MULTIPLY, MultiplyOperation),
        (CalculationType.DIVIDE, DivideOperation),
        ("Add", AddOperation),
        ("sub", SubOperation),
        ("MULTIPLY", MultiplyOperation),
        ("divide", DivideOperation),
    ],
)
def test_factory_chooses_correct_operation(calc_type, expected_class):
    assert isinstance(CalculationFactory.get_operation(calc_type), expected_class)


@pytest.mark.parametrize(
    "calc_type, a, b, expected",
    [
        ("Add", 2, 3, 5),
        ("Add", -2.5, 1.5, -1.0),
        ("Sub", 10, 4, 6),
        ("Sub", 1, 5, -4),
        ("Multiply", 6, 7, 42),
        ("Multiply", -3, 0, 0),
        ("Divide", 10, 4, 2.5),
        ("Divide", 0, 5, 0),
    ],
)
def test_each_operation_result(calc_type, a, b, expected):
    assert CalculationFactory.compute(calc_type, a, b) == pytest.approx(expected)


def test_divide_by_zero_raises():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        CalculationFactory.compute("Divide", 1, 0)


@pytest.mark.parametrize("bad_type", ["Power", "", "   ", None, 5])
def test_unsupported_type_raises(bad_type):
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        CalculationFactory.get_operation(bad_type)


def test_factory_is_extensible(monkeypatch):
    """New operations can be registered without changing existing code."""

    class PowerOperation(Operation):
        def execute(self, a, b):
            return a ** b

    monkeypatch.setitem(CalculationFactory._registry, "power", PowerOperation)
    assert CalculationFactory.compute("Power", 2, 3) == 8
