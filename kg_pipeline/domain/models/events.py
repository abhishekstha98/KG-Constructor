from pydantic import BaseModel, Field
from typing import Dict, List, Set, Any
from ..domain.enums import RoleType

class SemanticRoleFrame(BaseModel):
    """Represent raw SRL output before canonicalization."""
    frame_id: str
    predicate_text: str
    sentence_id: str
    arguments: Dict[RoleType, List[str]] = Field(default_factory=dict)

class EventRecord(BaseModel):
    """Represent an event at the document level."""
    event_id: str
    event_type: str
    trigger_text: str
    sentence_id: str
    participants: Dict[RoleType, List[str]] = Field(default_factory=dict)

class AlignedEvent(BaseModel):
    """Represent a canonicalized event linked to URIs."""
    aligned_event_id: str
    event_type_uri: str
    merged_participants: Dict[str, List[str]] = Field(default_factory=dict)
    source_event_ids: Set[str] = Field(default_factory=set)
