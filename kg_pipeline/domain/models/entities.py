from pydantic import BaseModel, Field
from typing import List, Set, Optional
from ..domain.enums import EntityType

class Mention(BaseModel):
    """Represent a specific occurrence of an entity in the text."""
    mention_id: str
    text: str
    sentence_id: str
    start_char: int
    end_char: int

class Entity(BaseModel):
    """Represent an entity at the document level."""
    entity_id: str
    canonical_name: str
    entity_type: EntityType
    mentions: List[Mention] = Field(default_factory=list)

class CanonicalEntity(BaseModel):
    """Represent a canonicalized entity linked to a URI/Knowledge Base."""
    canonical_id: str
    uri: str
    primary_name: str
    entity_type: EntityType
    aliases: Set[str] = Field(default_factory=set)
    source_entity_ids: Set[str] = Field(default_factory=set)

class NounPhraseUnit(BaseModel):
    """Represent a noun phrase that might or might not be a named entity."""
    np_id: str
    text: str
    sentence_id: str
    linked_entity_id: Optional[str] = None
