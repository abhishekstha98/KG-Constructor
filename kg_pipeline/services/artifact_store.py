import os
import logging
from typing import Optional
from ..domain.models.artifacts import ArtifactEnvelope
from ..storage.file_store import FileStore

logger = logging.getLogger(__name__)

class ArtifactStore:
    """
    Standardizes the persistence and retrieval of stage artifacts.
    
    Artifacts are stored in a hierarchical directory structure:
    output_dir/run_id/doc_id/stage_name.json
    """
    
    def __init__(self, storage_provider: FileStore, base_path: str):
        self.storage = storage_provider
        self.base_path = base_path

    def _get_path(self, artifact: ArtifactEnvelope) -> str:
        return os.path.join(
            self.base_path,
            artifact.pipeline_run_id,
            artifact.document_id,
            f"{artifact.stage_name}.json"
        )

    def save_artifact(self, artifact: ArtifactEnvelope):
        """Persist an artifact to storage."""
        path = self._get_path(artifact)
        data = artifact.model_dump()
        self.storage.write(path, data)
        logger.info(f"Artifact persisted to {path}")

    def load_artifact(self, run_id: str, doc_id: str, stage_name: str) -> Optional[ArtifactEnvelope]:
        """Retrieve an artifact from storage."""
        path = os.path.join(self.base_path, run_id, doc_id, f"{stage_name}.json")
        data = self.storage.read(path)
        if data:
            return ArtifactEnvelope.model_validate(data)
        return None
