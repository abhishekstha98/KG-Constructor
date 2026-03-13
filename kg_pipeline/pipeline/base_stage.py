from abc import ABC, abstractmethod
from typing import Type, Any, Optional
from pydantic import BaseModel
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.enums import StageName

class BaseStage(ABC):
    """
    Abstract base class for all pipeline stages.
    
    Each stage is responsible for:
    1. Validating input schema.
    2. Processing logic.
    3. Emitting a standardized ArtifactEnvelope with provenance.
    """

    @property
    @abstractmethod
    def phase_name(self) -> StageName:
        """Return the StageName enum value for this phase."""
        pass

    @property
    @abstractmethod
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        """Return the Pydantic type expected for the payload from the previous stage."""
        pass

    @property
    @abstractmethod
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        """Return the Pydantic type produced by this stage."""
        pass

    @abstractmethod
    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        """
        Execute core stage logic.
        
        Args:
            input_artifact: Standard envelope from previous stage.
            
        Returns:
            The raw data or Pydantic model payload for this stage.
        """
        pass

    def run(self, input_artifact: ArtifactEnvelope) -> ArtifactEnvelope:
        """
        Wrapper around execute that handles validation and envelope wrapping.
        """
        # (Input Schema Validation TBD)
        
        result_payload = self.execute(input_artifact)
        
        return ArtifactEnvelope(
            pipeline_run_id=input_artifact.pipeline_run_id,
            document_id=input_artifact.document_id,
            stage_name=self.phase_name.value,
            input_artifact_refs=[input_artifact.stage_name],
            payload=result_payload
        )
