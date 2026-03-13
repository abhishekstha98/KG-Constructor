import logging
from typing import List, Optional
from ..domain.enums import StageName
from ..domain.models.artifacts import ArtifactEnvelope
from .registry import StageRegistry
from ..services.artifact_store import ArtifactStore

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """
    Manages the sequential execution of registered stages.
    
    Responsible for checkpointing artifacts between stages using the ArtifactStore
    and ensuring the output of phase N flows into the input of phase N+1.
    """
    
    def __init__(self, artifact_store: ArtifactStore):
        self.artifact_store = artifact_store
        self.ordered_stages = [
            StageName.PHASE00_SCHEMA_BOOTSTRAP,
            StageName.PHASE01_DOCUMENT_NORMALIZATION,
            StageName.PHASE02_SENTENCE_PREPARATION,
            StageName.PHASE03_ENTITY_EXTRACTION,
            StageName.PHASE04_ENTITY_CANONICALIZATION,
            StageName.PHASE05_NP_GROUPING,
            StageName.PHASE06_RELATION_EXTRACTION,
            StageName.PHASE07_SRL,
            StageName.PHASE08_ROLE_ALIGNMENT,
            StageName.PHASE09_PREDICATE_MAPPING,
            StageName.PHASE10_RDF_GENERATION,
            StageName.PHASE11_VALIDATION_REPAIR,
            StageName.PHASE12_EXPORT
        ]

    def run_pipeline(self, run_id: str, initial_artifact: ArtifactEnvelope) -> ArtifactEnvelope:
        """
        Executes the full chain of stages for a single document.
        """
        current_artifact = initial_artifact
        
        for stage_name in self.ordered_stages:
            logger.info(f"Starting stage: {stage_name.value}")
            
            # 1. Instantiate stage
            stage_cls = StageRegistry.get_stage(stage_name)
            stage_instance = stage_cls()
            
            # 2. Execute stage
            current_artifact = stage_instance.run(current_artifact)
            
            # 3. Persist checkpoint
            self.artifact_store.save_artifact(current_artifact)
            
            logger.info(f"Completed stage: {stage_name.value}")
            
        return current_artifact
