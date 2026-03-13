from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from .common import ConfidenceSummary, WarningRecord, ErrorRecord

class ArtifactEnvelope(BaseModel):
    """
    The core data structure passed between pipeline stages.
    
    Contains the standardized metadata envelope and a polymorphic payload
    representing the current state of extraction.
    """
    pipeline_run_id: str = Field(description="Unique identifier for the entire pipeline run.")
    document_id: str = Field(description="The source document being processed.")
    stage_name: str = Field(description="The name of the pipeline stage that produced this artifact.")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO 8601 timestamp of creation.")
    
    input_artifact_refs: List[str] = Field(default_factory=list, description="IDs of artifacts consumed to produce this one.")
    output_version: str = Field(default="1.0", description="Version of the output schema.")
    
    payload: Any = Field(description="The actual data produced by the stage. Typed internally or treated as dict in base.")
    
    confidence_summary: ConfidenceSummary = Field(default_factory=ConfidenceSummary, description="Aggregation of confidence scores.")
    warnings: List[WarningRecord] = Field(default_factory=list, description="Non-fatal anomalies detected.")
    errors: List[ErrorRecord] = Field(default_factory=list, description="Fatal errors that block further processing.")
