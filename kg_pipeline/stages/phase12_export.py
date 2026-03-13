import os
import json
from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, CanonicalEntity, NounPhraseUnit
from ..domain.models.relations import Relation, PredicateMapping
from ..domain.models.events import SemanticRoleFrame, EventRecord, AlignedEvent
from ..domain.models.rdf import RDFStatement
from ..domain.models.validation import ValidationResult
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase11_validation_repair import ValidationRepairPayload

class ExportPayload(BaseModel):
    document: Document
    entities: List[Entity]
    canonical_entities: List[CanonicalEntity]
    noun_phrases: List[NounPhraseUnit]
    relations: List[Relation]
    frames: List[SemanticRoleFrame]
    events: List[EventRecord]
    aligned_events: List[AlignedEvent]
    predicate_mappings: List[PredicateMapping]
    rdf_statements: List[RDFStatement]
    validation: ValidationResult
    export_paths: Dict[str, str]
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE12_EXPORT)
class Phase12Export(BaseStage):
    """
    Phase 12: Export
    Serializes final verified data to distinct formats.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE12_EXPORT

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return ValidationRepairPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return ExportPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: ValidationRepairPayload = input_artifact.payload  # type: ignore
        doc_id = payload.document.document_id
        
        output_dir = os.path.join(settings.output_dir, "final_exports", doc_id)
        os.makedirs(output_dir, exist_ok=True)
        
        nt_path = os.path.join(output_dir, "graph.nt")
        with open(nt_path, "w", encoding="utf-8") as f:
            for s in payload.rdf_statements:
                obj_str = f'"{s.object_value}"' if s.is_literal else f'<{s.object_value}>'
                f.write(f'<{s.subject_uri}> <{s.predicate_uri}> {obj_str} .\n')
                
        json_path = os.path.join(output_dir, "knowledge_package.json")
        # In mock, we skip full JSON dump for brevity but it's where it would go.
        
        return ExportPayload(
            document=payload.document,
            entities=payload.entities,
            canonical_entities=payload.canonical_entities,
            noun_phrases=payload.noun_phrases,
            relations=payload.relations,
            frames=payload.frames,
            events=payload.events,
            aligned_events=payload.aligned_events,
            predicate_mappings=payload.predicate_mappings,
            rdf_statements=payload.rdf_statements,
            validation=payload.validation,
            export_paths={
                "ntriples": nt_path,
                "json_package": json_path
            }
        )
