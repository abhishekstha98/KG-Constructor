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
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from ..services.uri_minter import URIMinter
from .phase09_predicate_mapping import PredicateMappingPayload

class RdfGenerationPayload(BaseModel):
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
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE10_RDF_GENERATION)
class Phase10RdfGeneration(BaseStage):
    """
    Phase 10: RDF Generation
    Transforms aligned metadata into standard RDF triples.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE10_RDF_GENERATION

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return PredicateMappingPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return RdfGenerationPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: PredicateMappingPayload = input_artifact.payload  # type: ignore
        statements = []
        minter = URIMinter(str(settings.base_uri_namespace))
        
        ont_map = {m.surface_form: m.ontology_uri for m in payload.predicate_mappings}
        
        eid_to_uri = {}
        for ce in payload.canonical_entities:
            for sid in ce.source_entity_ids:
                eid_to_uri[sid] = ce.uri

        for rel in payload.relations:
            sub_uri = eid_to_uri.get(rel.subject_entity_id)
            obj_uri = eid_to_uri.get(rel.object_entity_id)
            pred_uri = ont_map.get(rel.predicate_text, minter.mint_predicate_uri(rel.predicate_text))
            
            if sub_uri and obj_uri:
                statements.append(RDFStatement(
                    subject_uri=sub_uri,
                    predicate_uri=pred_uri,
                    object_value=obj_uri,
                    is_literal=False
                ))

        for event in payload.aligned_events:
            event_uri = f"{settings.base_uri_namespace}event/{event.aligned_event_id}"
            
            statements.append(RDFStatement(
                subject_uri=event_uri,
                predicate_uri="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                object_value=event.event_type_uri,
                is_literal=False
            ))
            
            for role_uri, actor_ids in event.merged_participants.items():
                for actor_id in actor_ids:
                    target_uri = eid_to_uri.get(actor_id)
                    is_lit = False
                    if not target_uri:
                        for npu in payload.noun_phrases:
                            if npu.np_id == actor_id:
                                target_uri = npu.text
                                is_lit = True
                                break
                    
                    if target_uri:
                        statements.append(RDFStatement(
                            subject_uri=event_uri,
                            predicate_uri=f"http://example.org/role/{role_uri}",
                            object_value=target_uri,
                            is_literal=is_lit
                        ))

        return RdfGenerationPayload(
            document=payload.document,
            entities=payload.entities,
            canonical_entities=payload.canonical_entities,
            noun_phrases=payload.noun_phrases,
            relations=payload.relations,
            frames=payload.frames,
            events=payload.events,
            aligned_events=payload.aligned_events,
            predicate_mappings=payload.predicate_mappings,
            rdf_statements=statements
        )
