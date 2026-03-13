from pydantic import BaseModel, Field
from typing import Union, Optional

class RDFStatement(BaseModel):
    """Represent a single RDF triple."""
    subject_uri: str
    predicate_uri: str
    object_value: str
    is_literal: bool = False
    datatype: Optional[str] = None
    language: Optional[str] = None
