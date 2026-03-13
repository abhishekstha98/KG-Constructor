from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document
from ..domain.models.entities import Entity, CanonicalEntity
from ..services.uri_minter import URIMinter
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry
from .phase03_entity_extraction import EntityExtractionPayload

class EntityCanonicalizationPayload(BaseModel):
    document: Document
    entities: List[Entity]
    canonical_entities: List[CanonicalEntity]
    model_config = ConfigDict(arbitrary_types_allowed=True)

@StageRegistry.register(StageName.PHASE04_ENTITY_CANONICALIZATION)
class Phase04EntityCanonicalization(BaseStage):
    """
    Phase 04: Entity Canonicalization
    Links document-level entities to a global ontology/KB or mints new stable IRIs.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE04_ENTITY_CANONICALIZATION

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return EntityExtractionPayload

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return EntityCanonicalizationPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        payload: EntityExtractionPayload = input_artifact.payload  # type: ignore
        minter = URIMinter(str(settings.base_uri_namespace))
        
        canonical_entities: Dict[str, CanonicalEntity] = {}
        
        merge_map = {
            "Global Tech": "Global Tech Corp",
            "AI Innovators": "AI Innovators Ltd"
        }
        
        for entity in payload.entities:
            target_name = merge_map.get(entity.canonical_name, entity.canonical_name)
            
            canonical_uri = minter.mint_entity_uri(target_name, entity.entity_type.value)
            
            if canonical_uri not in canonical_entities:
                canonical_entities[canonical_uri] = CanonicalEntity(
                    canonical_id=f"canon_e_{len(canonical_entities)}",
                    uri=canonical_uri,
                    primary_name=target_name,
                    entity_type=entity.entity_type,
                    aliases={entity.canonical_name},
                    source_entity_ids={entity.entity_id}
                )
            else:
                canonical_entities[canonical_uri].aliases.add(entity.canonical_name)
                canonical_entities[canonical_uri].source_entity_ids.add(entity.entity_id)

        return EntityCanonicalizationPayload(
            document=payload.document,
            entities=payload.entities,
            canonical_entities=list(canonical_entities.values())
        )
