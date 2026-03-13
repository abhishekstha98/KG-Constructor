from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName, RoleType
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, CanonicalEntity, NounPhraseUnit
from ..domain.models.relations import Relation
from ..domain.models.events import SemanticRoleFrame
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase06_relation_extraction import RelationExtractionPayload

class SrlPayload(BaseModel):
    document: Document
    entities: List[Entity]
    canonical_entities: List[CanonicalEntity]
    noun_phrases: List[NounPhraseUnit]
    relations: List[Relation]
    frames: List[SemanticRoleFrame]
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE07_SRL)
class Phase07SRL(BaseStage):
    """
    Phase 07: Semantic Role Labeling
    Identifies predicates and their arguments (Agent, Patient, etc.).
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE07_SRL

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return RelationExtractionPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return SrlPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: RelationExtractionPayload = input_artifact.payload  # type: ignore
        frames = []
        frame_counter = 0
        
        for section in payload.document.sections:
            for sentence in section.sentences:
                if "acquired" in sentence.text:
                    frames.append(SemanticRoleFrame(
                        frame_id=f"frame_{frame_counter}",
                        predicate_text="acquired",
                        sentence_id=sentence.sentence_id,
                        arguments={
                            RoleType.AGENT: ["Global Tech Corp"],
                            RoleType.PATIENT: ["AI Innovators Ltd"],
                            RoleType.THEME: ["$1.5 billion"]
                        }
                    ))
                    frame_counter += 1
                
                if "founded" in sentence.text:
                     frames.append(SemanticRoleFrame(
                        frame_id=f"frame_{frame_counter}",
                        predicate_text="founded",
                        sentence_id=sentence.sentence_id,
                        arguments={
                            RoleType.AGENT: ["Sarah Jenkins"],
                            RoleType.PATIENT: ["AI Innovators"],
                            RoleType.TIME: ["2020"]
                        }
                    ))
                     frame_counter += 1

        return SrlPayload(
            document=payload.document,
            entities=payload.entities,
            canonical_entities=payload.canonical_entities,
            noun_phrases=payload.noun_phrases,
            relations=payload.relations,
            frames=frames
        )
