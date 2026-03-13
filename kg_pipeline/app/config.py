import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl
from typing import Dict, Any

class PipelineConfig(BaseSettings):
    """Central configuration for the KG Pipeline."""
    
    # Project Settings
    project_name: str = "Automated OIE KG Pipeline"
    
    # Base URI for canonical entities
    base_uri_namespace: HttpUrl = Field(default="http://example.org/kg/") # type: ignore
    
    # Directories
    data_dir: str = Field(default="data")
    input_dir: str = Field(default="data/input")
    intermediate_dir: str = Field(default="data/intermediate")
    output_dir: str = Field(default="data/output")
    prompts_dir: str = Field(default="prompts")
    
    # LLM & Retry Settings
    llm_mock_mode: bool = Field(default=True, description="If true, use the mock LLM client.")
    max_retries: int = Field(default=3, description="Global max retries for failed LLM calls.")
    
    # Stage Enablement (Can toggle specific stages on/off)
    enabled_stages: set[str] = Field(default_factory=lambda: {
        "phase00_schema_bootstrap",
        "phase01_document_normalization",
        "phase02_sentence_preparation",
        "phase03_entity_extraction",
        "phase04_entity_canonicalization",
        "phase05_np_grouping",
        "phase06_relation_extraction",
        "phase07_srl",
        "phase08_role_alignment",
        "phase09_predicate_mapping",
        "phase10_rdf_generation",
        "phase11_validation_repair",
        "phase12_export"
    })
    
    # Default minimum confidence thresholds (0.0 to 1.0)
    confidence_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "entity": 0.5,
            "relation": 0.5,
            "canonicalization": 0.7,
            "default": 0.6
        }
    )

    model_config = SettingsConfigDict(
        env_prefix="KG_", 
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Global settings instance
settings = PipelineConfig()
