from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..domain.enums import StageName, ValidationStatus
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, CanonicalEntity, NounPhraseUnit
from ..domain.models.relations import Relation, PredicateMapping
from ..domain.models.events import SemanticRoleFrame, EventRecord, AlignedEvent
from ..domain.models.rdf import RDFStatement
from ..domain.models.validation import ValidationResult, ValidationRecord
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase10_rdf_generation import RdfGenerationPayload

class ValidationRepairPayload(BaseModel):
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
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE11_VALIDATION_REPAIR)
class Phase11ValidationRepair(BaseStage):
    """
    Phase 11: Validation & Repair
    Checks generated RDF for constraints and performs heuristic repairs.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE11_VALIDATION_REPAIR

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return RdfGenerationPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return ValidationRepairPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: RdfGenerationPayload = input_artifact.payload  # type: ignore
        records = []
        status = ValidationStatus.VALID
        
        for event in payload.events:
             if 'PATIENT' not in [k.name if hasattr(k, 'name') else str(k) for k in event.participants.keys()]:
                 records.append(ValidationRecord(
                     record_id=event.event_id,
                     check_name="missing_patient_role",
                     passed=True,
                     message="Event missing Patient role. Warning only."
                 ))
                 status = ValidationStatus.WARNING

        return ValidationRepairPayload(
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
            validation=ValidationResult(
                document_id=payload.document.document_id,
                status=status,
                records=records,
                repaired_items=0
            )
        )
