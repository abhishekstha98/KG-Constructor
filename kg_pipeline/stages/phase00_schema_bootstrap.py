from typing import Optional, Type, Any, Dict, List
from pydantic import BaseModel, ConfigDict
from ..app.config import settings
from ..domain.enums import StageName, EntityType, RoleType
from ..domain.models.artifacts import ArtifactEnvelope
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry

class DomainSchemaPayload(BaseModel):
    allowed_entity_types: List[str]
    allowed_roles: List[str]
    minimum_confidence: float
    base_uri: str
    model_config = ConfigDict(arbitrary_types_allowed=True)


@StageRegistry.register(StageName.PHASE00_SCHEMA_BOOTSTRAP)
class Phase00SchemaBootstrap(BaseStage):
    """
    Phase 00: Schema Bootstrap
    Initializes the extraction run by declaring the explicit domain constraints
    the pipeline rules and LLMs should adhere to.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE00_SCHEMA_BOOTSTRAP

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return dict  # Usually empty dict or initial request payload containing raw text

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return DomainSchemaPayload

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        return DomainSchemaPayload(
            allowed_entity_types=[e.value for e in EntityType],
            allowed_roles=[r.value for r in RoleType],
            minimum_confidence=settings.confidence_thresholds.get("default", 0.5),
            base_uri=str(settings.base_uri_namespace)
        )
