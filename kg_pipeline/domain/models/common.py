from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ProvenanceBlock(BaseModel):
    """Information about how a piece of data was generated."""
    generating_stage: str = Field(description="The stage that generated this data.")
    timestamp: float = Field(description="Unix timestamp of creation.")
    method: str = Field(description="Method used for generation (e.g., 'llm_extraction', 'rule_based').")
    model_name: Optional[str] = Field(default=None, description="Name of the model if an LLM was used.")
    prompt_version: Optional[str] = Field(default=None, description="Version of the prompt used.")
    system_version: str = Field(default="0.1.0", description="Version of the KG pipeline system.")

class ConfidenceSummary(BaseModel):
    """A summary of confidence scores for an artifact."""
    overall_score: float = Field(default=1.0, description="Overall confidence score between 0.0 and 1.0.")
    component_scores: Dict[str, float] = Field(default_factory=dict, description="Granular scores for specific components.")
    
class WarningRecord(BaseModel):
    """A warning generated during pipeline execution."""
    code: str = Field(description="Warning code or identifier.")
    message: str = Field(description="Human-readable warning message.")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context about the warning.")

class ErrorRecord(BaseModel):
    """An error generated during pipeline execution."""
    code: str = Field(description="Error code or identifier.")
    message: str = Field(description="Human-readable error message.")
    traceback: Optional[str] = Field(default=None, description="Stack trace or execution context.")
    fatal: bool = Field(default=False, description="Whether this error is fatal for the pipeline run.")
