from pydantic import BaseModel, Field
from typing import List, Optional, Any
from ..domain.enums import ValidationStatus

class ValidationRecord(BaseModel):
    """Represent the result of a single validation check."""
    record_id: str
    check_name: str
    passed: bool
    message: Optional[str] = None
    repaired: bool = False

class ValidationResult(BaseModel):
    """Aggregation of all validation checks for a document."""
    document_id: str
    status: ValidationStatus
    records: List[ValidationRecord] = Field(default_factory=list)
    repaired_items: int = 0
