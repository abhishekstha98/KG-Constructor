from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName, RoleType
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, CanonicalEntity, NounPhraseUnit
from ..domain.models.relations import Relation
from ..domain.models.events import SemanticRoleFrame, EventRecord, AlignedEvent
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase07_srl import SrlPayload

class RoleAlignmentPayload(BaseModel):
    document: Document
    entities: List[Entity]
    canonical_entities: List[CanonicalEntity]
    noun_phrases: List[NounPhraseUnit]
    relations: List[Relation]
    frames: List[SemanticRoleFrame]
    events: List[EventRecord]
    aligned_events: List[AlignedEvent]
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE08_ROLE_ALIGNMENT)
class Phase08RoleAlignment(BaseStage):
    """
    Phase 08: Role Alignment
    Maps semantic roles (frames) to concrete canonical entities or NP units.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE08_ROLE_ALIGNMENT

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return SrlPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return RoleAlignmentPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: SrlPayload = input_artifact.payload  # type: ignore
        events = []
        aligned_events = []
        
        def find_entity_id(name: str) -> Optional[str]:
            for e in payload.entities:
                if name.lower() in e.canonical_name.lower():
                    return e.entity_id
            return None

        for frame in payload.frames:
            participants: Dict[RoleType, List[str]] = {}
            for role, args in frame.arguments.items():
                aligned_ids = []
                for arg_text in args:
                    eid = find_entity_id(arg_text)
                    if eid:
                        aligned_ids.append(eid)
                    else:
                        for npu in payload.noun_phrases:
                            if arg_text.lower() == npu.text.lower():
                                aligned_ids.append(npu.np_id)
                                break
                if aligned_ids:
                    participants[role] = aligned_ids
            
            event_id = f"ev_{frame.frame_id}"
            events.append(EventRecord(
                event_id=event_id,
                event_type=frame.predicate_text,
                trigger_text=frame.predicate_text,
                sentence_id=frame.sentence_id,
                participants=participants
            ))
            
            aligned_events.append(AlignedEvent(
                aligned_event_id=f"aligned_{event_id}",
                event_type_uri=f"http://example.org/event/{frame.predicate_text}",
                merged_participants={str(k.value): v for k, v in participants.items()},
                source_event_ids={event_id}
            ))

        return RoleAlignmentPayload(
            document=payload.document,
            entities=payload.entities,
            canonical_entities=payload.canonical_entities,
            noun_phrases=payload.noun_phrases,
            relations=payload.relations,
            frames=payload.frames,
            events=events,
            aligned_events=aligned_events
        )
