# app/schemas/calculation.py
"""
Calculation Pydantic Schemas

- CalculationCreate: validates incoming data (a, b, type).
- CalculationRead:   serializes a stored calculation back to the client.

Validation rules
----------------
* ``type`` must be one of Add, Sub, Multiply, Divide (case-insensitive).
* ``a`` and ``b`` must be finite numbers (no NaN / Infinity).
* Division by zero (``type == Divide`` and ``b == 0``) is rejected.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CalculationType(str, Enum):
    """The supported calculation types."""

    ADD = "Add"
    SUB = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


class CalculationCreate(BaseModel):
    """Schema for the data needed to create a calculation."""

    a: float = Field(..., allow_inf_nan=False, description="First operand", examples=[10])
    b: float = Field(..., allow_inf_nan=False, description="Second operand", examples=[2])
    type: CalculationType = Field(
        ..., description="Operation: Add, Sub, Multiply or Divide", examples=["Add"]
    )
    user_id: Optional[UUID] = Field(
        default=None, description="Optional owner of the calculation (FK to users.id)"
    )

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        """Accept the type case-insensitively ("add" -> "Add") and reject non-strings."""
        allowed = {t.value.lower(): t.value for t in CalculationType}
        if isinstance(value, CalculationType):
            return value
        if not isinstance(value, str) or value.strip().lower() not in allowed:
            raise ValueError(
                f"Type must be one of: {', '.join(t.value for t in CalculationType)}"
            )
        return allowed[value.strip().lower()]

    @model_validator(mode="after")
    def check_no_division_by_zero(self) -> "CalculationCreate":
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self

    model_config = ConfigDict(
        json_schema_extra={"example": {"a": 10, "b": 2, "type": "Divide"}}
    )


class CalculationRead(BaseModel):
    """Schema returned to clients. Only calculation data - nothing about the user
    other than their id."""

    id: UUID
    a: float
    b: float
    type: CalculationType
    result: Optional[float] = None
    user_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
