# app/models/calculation.py
"""
Calculation SQLAlchemy model.

Design decision: the ``result`` is **stored** when the row is created (computed
through the factory), so reads never need to recompute it. ``user_id`` is an
optional foreign key to ``users.id``.

Database-level CHECK constraints back up the Pydantic validation, so bad data is
rejected even if something bypasses the schemas.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.operations.factory import CalculationFactory
from app.schemas.calculation import CalculationType


class Calculation(Base):
    __tablename__ = "calculations"
    __table_args__ = (
        CheckConstraint(
            "type IN ('Add', 'Sub', 'Multiply', 'Divide')", name="ck_calculations_type"
        ),
        CheckConstraint(
            "NOT (type = 'Divide' AND b = 0)", name="ck_calculations_no_divide_by_zero"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False, index=True)
    result = Column(Float, nullable=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="calculations")

    def compute_result(self) -> float:
        """Compute the result from a, b and type using the factory."""
        return CalculationFactory.compute(self.type, self.a, self.b)

    @classmethod
    def create(
        cls,
        calculation_type,
        a: float,
        b: float,
        user_id: Optional[uuid.UUID] = None,
    ) -> "Calculation":
        """Build a Calculation with its result already computed.

        Raises:
            ValueError: unsupported type or division by zero.
        """
        operation_result = CalculationFactory.compute(calculation_type, a, b)
        type_value = (
            calculation_type.value
            if isinstance(calculation_type, CalculationType)
            else _canonical_type(calculation_type)
        )
        return cls(a=a, b=b, type=type_value, result=operation_result, user_id=user_id)

    def __repr__(self):
        return f"<Calculation(a={self.a}, b={self.b}, type={self.type}, result={self.result})>"


def _canonical_type(value: str) -> str:
    """Return the canonical spelling ("add" -> "Add") of a built-in type name;
    custom registered types are stored as given."""
    for member in CalculationType:
        if member.value.lower() == value.strip().lower():
            return member.value
    return value.strip()
