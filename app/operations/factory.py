# app/operations/factory.py
"""
Factory pattern for calculation logic.

``CalculationFactory`` maps a calculation type ("Add", "Sub", "Multiply",
"Divide") to the ``Operation`` class that implements it. New operations can be
added with ``CalculationFactory.register`` without touching existing code.
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, Union

from app.operations import add, subtract, multiply, divide
from app.schemas.calculation import CalculationType


class Operation(ABC):
    """Interface every calculation operation implements."""

    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """Return the result of applying the operation to a and b."""


class AddOperation(Operation):
    def execute(self, a: float, b: float) -> float:
        return add(a, b)


class SubOperation(Operation):
    def execute(self, a: float, b: float) -> float:
        return subtract(a, b)


class MultiplyOperation(Operation):
    def execute(self, a: float, b: float) -> float:
        return multiply(a, b)


class DivideOperation(Operation):
    def execute(self, a: float, b: float) -> float:
        return divide(a, b)  # raises ValueError when b == 0


class CalculationFactory:
    """Creates the right ``Operation`` for a calculation type."""

    # keyed by lower-case type name so lookups are case-insensitive
    _registry: Dict[str, Type[Operation]] = {
        CalculationType.ADD.value.lower(): AddOperation,
        CalculationType.SUB.value.lower(): SubOperation,
        CalculationType.MULTIPLY.value.lower(): MultiplyOperation,
        CalculationType.DIVIDE.value.lower(): DivideOperation,
    }

    @staticmethod
    def _key(calc_type: Union[str, CalculationType]) -> str:
        if isinstance(calc_type, CalculationType):
            return calc_type.value.lower()
        if isinstance(calc_type, str):
            return calc_type.strip().lower()
        return ""

    @classmethod
    def register(cls, calc_type: str, operation: Type[Operation]) -> None:
        """Register a new operation class for ``calc_type``."""
        cls._registry[cls._key(calc_type)] = operation

    @classmethod
    def get_operation(cls, calc_type: Union[str, CalculationType]) -> Operation:
        """Return an instance of the operation for ``calc_type``.

        Raises:
            ValueError: if the type is not supported.
        """
        operation = cls._registry.get(cls._key(calc_type))
        if operation is None:
            raise ValueError(f"Unsupported calculation type: {calc_type!r}")
        return operation()

    @classmethod
    def compute(cls, calc_type: Union[str, CalculationType], a: float, b: float) -> float:
        """Convenience helper: pick the operation and run it."""
        return cls.get_operation(calc_type).execute(a, b)
