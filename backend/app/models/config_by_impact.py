from pydantic import BaseModel, Field, validator

from .agregator import Agregator
from .manager import Manager
from .patterns import NEO4J_ID_PATTERN
from .validators import validate_max_level


class ConfigByImpactRequest(BaseModel):
    requirement_file_id: str = Field(
        pattern=NEO4J_ID_PATTERN
    )
    max_level: int = Field(...)
    impact: float = Field(
        ge=0,
        le=10
    )
    manager: Manager
    agregator: Agregator

    @validator("max_level")
    def validate_max_level(cls, value):
        return validate_max_level(value)
