from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName, EntityType
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, Mention
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry

class EntityExtractionPayload(BaseModel):
    document: Document
    entities: List[Entity]
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE03_ENTITY_EXTRACTION)
class Phase03EntityExtraction(BaseStage):
    """
    Phase 03: Entity Extraction
    Uses heuristics (or LLM) to find mentions of entities in the text.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE03_ENTITY_EXTRACTION

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return Document

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return EntityExtractionPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        doc: Document = input_artifact.payload  # type: ignore
        entities = []
        
        # Mock Deterministic Heuristics
        heuristics = {
            "Global Tech Corp": EntityType.ORGANIZATION,
            "Global Tech": EntityType.ORGANIZATION,
            "AI Innovators Ltd": EntityType.ORGANIZATION,
            "AI Innovators": EntityType.ORGANIZATION,
            "Sarah Jenkins": EntityType.PERSON,
            "London": EntityType.LOCATION,
            "San Francisco": EntityType.LOCATION,
            "Cloud Suite": EntityType.CONCEPT,
            "Michael Chang": EntityType.PERSON
        }
        
        entity_counter = 0
        mention_counter = 0
        
        surface_to_mentions: Dict[str, List[Mention]] = {}
        
        for section in doc.sections:
            for sentence in section.sentences:
                for target, e_type in heuristics.items():
                    start_idx = sentence.text.lower().find(target.lower())
                    if start_idx != -1:
                        mention = Mention(
                            mention_id=f"m_{mention_counter}",
                            text=sentence.text[start_idx : start_idx + len(target)],
                            sentence_id=sentence.sentence_id,
                            start_char=start_idx,
                            end_char=start_idx + len(target)
                        )
                        surface_to_mentions.setdefault(target, []).append(mention)
                        mention_counter += 1

        for surface, m_list in surface_to_mentions.items():
            entities.append(Entity(
                entity_id=f"e_{entity_counter}",
                canonical_name=surface,
                entity_type=heuristics[surface],
                mentions=m_list
            ))
            entity_counter += 1
            
        return EntityExtractionPayload(
            document=doc,
            entities=entities
        )
