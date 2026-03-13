from pydantic import BaseModel, Field
from typing import Optional

class Relation(BaseModel):
    """Represent a binary relation extracted from a sentence."""
    relation_id: str
    predicate_text: str
    subject_entity_id: str
    object_entity_id: str
    sentence_id: str
    confidence: float = 1.0

class PredicateMapping(BaseModel):
    """Represent a mapping of a surface predicate to an ontology URI."""
    mapping_id: str
    surface_form: str
    ontology_uri: str
    source: str = "custom"
