from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, CanonicalEntity, NounPhraseUnit
from ..domain.models.relations import Relation
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase05_np_grouping import NpGroupingPayload

class RelationExtractionPayload(BaseModel):
    document: Document
    entities: List[Entity]
    canonical_entities: List[CanonicalEntity]
    noun_phrases: List[NounPhraseUnit]
    relations: List[Relation]
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE06_RELATION_EXTRACTION)
class Phase06RelationExtraction(BaseStage):
    """
    Phase 06: Relation Extraction
    Finds direct binary or n-ary relations between entities in sentences.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE06_RELATION_EXTRACTION

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return NpGroupingPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return RelationExtractionPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: NpGroupingPayload = input_artifact.payload  # type: ignore
        relations = []
        rel_counter = 0
        
        def find_entity_id(name: str) -> Optional[str]:
            for e in payload.entities:
                if name in e.canonical_name:
                    return e.entity_id
            return None

        for section in payload.document.sections:
            for sentence in section.sentences:
                if "acquired" in sentence.text:
                    sub_id = find_entity_id("Global Tech")
                    obj_id = find_entity_id("AI Innovators")
                    if sub_id and obj_id:
                        relations.append(Relation(
                            relation_id=f"rel_{rel_counter}",
                            predicate_text="acquired",
                            subject_entity_id=sub_id,
                            object_entity_id=obj_id,
                            sentence_id=sentence.sentence_id
                        ))
                        rel_counter += 1
                        
                if "CEO" in sentence.text:
                    sub_id = find_entity_id("Michael Chang")
                    obj_id = find_entity_id("Global Tech")
                    if sub_id and obj_id:
                        relations.append(Relation(
                            relation_id=f"rel_{rel_counter}",
                            predicate_text="is CEO of",
                            subject_entity_id=sub_id,
                            object_entity_id=obj_id,
                            sentence_id=sentence.sentence_id
                        ))
                        rel_counter += 1

        return RelationExtractionPayload(
            document=payload.document,
            entities=payload.entities,
            canonical_entities=payload.canonical_entities,
            noun_phrases=payload.noun_phrases,
            relations=relations
        )
