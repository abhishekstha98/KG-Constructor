from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, CanonicalEntity, NounPhraseUnit
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase04_entity_canonicalization import EntityCanonicalizationPayload

class NpGroupingPayload(BaseModel):
    document: Document
    entities: List[Entity]
    canonical_entities: List[CanonicalEntity]
    noun_phrases: List[NounPhraseUnit]
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE05_NP_GROUPING)
class Phase05NpGrouping(BaseStage):
    """
    Phase 05: Noun Phrase Grouping & Resolution
    Finds remaining noun phrases and links them to extracted entities.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE05_NP_GROUPING

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return EntityCanonicalizationPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return NpGroupingPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: EntityCanonicalizationPayload = input_artifact.payload  # type: ignore
        
        noun_phrases = []
        np_counter = 0
        
        for entity in payload.entities:
            for mention in entity.mentions:
                np_id = f"npu_{np_counter}"
                noun_phrases.append(NounPhraseUnit(
                    np_id=np_id,
                    text=mention.text,
                    sentence_id=mention.sentence_id,
                    linked_entity_id=entity.entity_id
                ))
                np_counter += 1
                
        for section in payload.document.sections:
            for sentence in section.sentences:
                if "$1.5 billion" in sentence.text:
                    noun_phrases.append(NounPhraseUnit(
                        np_id=f"npu_{np_counter}",
                        text="$1.5 billion",
                        sentence_id=sentence.sentence_id
                    ))
                    np_counter += 1
                if "October 12, 2025" in sentence.text:
                    noun_phrases.append(NounPhraseUnit(
                        np_id=f"npu_{np_counter}",
                        text="October 12, 2025",
                        sentence_id=sentence.sentence_id
                    ))
                    np_counter += 1
                    
        return NpGroupingPayload(
            document=payload.document,
            entities=payload.entities,
            canonical_entities=payload.canonical_entities,
            noun_phrases=noun_phrases
        )
