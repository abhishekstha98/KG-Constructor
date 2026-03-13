from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, CanonicalEntity, NounPhraseUnit
from ..domain.models.relations import Relation, PredicateMapping
from ..domain.models.events import SemanticRoleFrame, EventRecord, AlignedEvent
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase08_role_alignment import RoleAlignmentPayload

class PredicateMappingPayload(BaseModel):
    document: Document
    entities: List[Entity]
    canonical_entities: List[CanonicalEntity]
    noun_phrases: List[NounPhraseUnit]
    relations: List[Relation]
    frames: List[SemanticRoleFrame]
    events: List[EventRecord]
    aligned_events: List[AlignedEvent]
    predicate_mappings: List[PredicateMapping]
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE09_PREDICATE_MAPPING)
class Phase09PredicateMapping(BaseStage):
    """
    Phase 09: Predicate Mapping
    Maps raw relational predicates and event types to an explicit ontology.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE09_PREDICATE_MAPPING

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return RoleAlignmentPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return PredicateMappingPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: RoleAlignmentPayload = input_artifact.payload  # type: ignore
        mappings = []
        
        ontology_map = {
            "acquired": "https://schema.org/ownedThrough",
            "is CEO of": "https://schema.org/ceo",
            "founded": "https://schema.org/foundingDate"
        }
        
        mapping_counter = 0
        for rel in payload.relations:
            if rel.predicate_text in ontology_map:
                mappings.append(PredicateMapping(
                    mapping_id=f"map_{mapping_counter}",
                    surface_form=rel.predicate_text,
                    ontology_uri=ontology_map[rel.predicate_text],
                    source="SCHEMA_ORG"
                ))
                mapping_counter += 1
                
        return PredicateMappingPayload(
            document=payload.document,
            entities=payload.entities,
            canonical_entities=payload.canonical_entities,
            noun_phrases=payload.noun_phrases,
            relations=payload.relations,
            frames=payload.frames,
            events=payload.events,
            aligned_events=payload.aligned_events,
            predicate_mappings=mappings
        )
