import os
import shutil
import pytest
from kg_pipeline.pipeline.orchestrator import PipelineOrchestrator
from kg_pipeline.services.artifact_store import ArtifactStore
from kg_pipeline.storage.json_store import JsonStore
from kg_pipeline.domain.models.artifacts import ArtifactEnvelope
from kg_pipeline.app.config import settings

def test_pipeline_end_to_end_mock():
    # Setup fresh output dir for test
    test_out = "data/test_output"
    if os.path.exists(test_out):
        shutil.rmtree(test_out)
    os.makedirs(test_out)
    
    # Initialize components
    file_store = JsonStore()
    artifact_store = ArtifactStore(file_store, test_out)
    orchestrator = PipelineOrchestrator(artifact_store)
    
    # Create initial artifact
    run_id = "test_run_e2e"
    doc_id = "test_doc"
    raw_text = "Global Tech Corp acquired AI Innovators in London on October 12, 2025."
    
    initial_artifact = ArtifactEnvelope(
        pipeline_run_id=run_id,
        document_id=doc_id,
        stage_name="init",
        payload={"text": raw_text}
    )
    
    # Run full pipeline
    final_artifact = orchestrator.run_pipeline(run_id, initial_artifact)
    
    # Assertions
    assert final_artifact.stage_name == "phase12_export"
    assert "export_paths" in final_artifact.payload
    
    nt_path = final_artifact.payload["export_paths"]["ntriples"]
    assert os.path.exists(nt_path)
    
    # Check that we actually extracted something (checking N-Triples file)
    with open(nt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) > 0
        # Check for our mock URIs
        content = "".join(lines)
        assert "Global_Tech_Corp" in content or "global_tech_corp" in content
        assert "acquired" in content
        
    # Cleanup
    shutil.rmtree(test_out)
