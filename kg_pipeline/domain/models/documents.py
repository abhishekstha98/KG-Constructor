from pydantic import BaseModel, Field
from typing import List, Optional

class Clause(BaseModel):
    """Represent a clause within a sentence."""
    clause_id: str
    text: str
    start_char: int
    end_char: int

class Sentence(BaseModel):
    """Represent a single sentence in a document."""
    sentence_id: str
    text: str
    start_char: int
    end_char: int
    clauses: List[Clause] = Field(default_factory=list)

class Section(BaseModel):
    """Represent a logical section of a document (e.g., Chapter, Paragraph)."""
    section_id: str
    title: Optional[str] = None
    text: str
    sentences: List[Sentence] = Field(default_factory=list)

class Document(BaseModel):
    """
    Standardized document model representing the results of 
    normalization and segmentation.
    """
    document_id: str
    title: str
    raw_text: str
    sections: List[Section] = Field(default_factory=list)
    language: str = "en"
