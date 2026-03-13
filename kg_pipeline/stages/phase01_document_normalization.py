import re
from typing import Optional, Type, Any
from pydantic import BaseModel
from ..app.config import settings
from ..domain.enums import StageName
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document, Section
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase00_schema_bootstrap import DomainSchemaPayload

@StageRegistry.register(StageName.PHASE01_DOCUMENT_NORMALIZATION)
class Phase01DocumentNormalization(BaseStage):
    """
    Phase 01: Document Normalization
    Takes raw textual input and produces a cleansed Document model.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE01_DOCUMENT_NORMALIZATION

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return DomainSchemaPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return Document

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        # Check if text was passed in current or input artifact
        raw_text = ""
        if isinstance(input_artifact.payload, dict):
            raw_text = input_artifact.payload.get("text", "")
            
        # If not in payload, check if there's a reference or we should fallback
        if not raw_text:
             try:
                # Fallback to sample for demo if payload is empty
                with open(f"{settings.input_dir}/sample.txt", "r", encoding="utf-8") as f:
                    raw_text = f.read()
             except:
                raw_text = "Global Tech Corp Acquisition of AI Innovators Ltd.\n\nOn October 12, 2025, Global Tech Corp acquired AI Innovators in London."
            
        # Clean text
        clean_text = re.sub(r'\n{3,}', '\n\n', raw_text.strip())
        
        # Simple heuristic section split by double newline
        blocks = clean_text.split('\n\n')
        sections = []
        for i, block in enumerate(blocks):
            sections.append(Section(
                section_id=f"sec_{i}",
                title=block.strip() if len(block) < 100 and i == 0 else None,
                text=block.strip(),
                sentences=[]
            ))
        
        return Document(
            document_id=input_artifact.document_id,
            title=sections[0].title if sections else "Untitled",
            raw_text=clean_text,
            sections=sections
        )
