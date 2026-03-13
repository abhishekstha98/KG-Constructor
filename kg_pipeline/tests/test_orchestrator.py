import pytest
from uuid import uuid4
from kg_pipeline.pipeline.orchestrator import PipelineOrchestrator
from kg_pipeline.services.artifact_store import ArtifactStore
from kg_pipeline.storage.json_store import JsonStore
from kg_pipeline.domain.models.artifacts import ArtifactEnvelope

def test_orchestrator_initialization():
    store = ArtifactStore(JsonStore(), "tests/tmp_out")
    orch = PipelineOrchestrator(store)
    
    # Check that it loaded a sequence
    assert len(orch.complete_sequence) > 0

def test_execution_plan_trimming():
    store = ArtifactStore(JsonStore(), "tests/tmp_out")
    orch = PipelineOrchestrator(store)
    
    # Should start from Phase 00 by default
    plan = orch._determine_execution_plan()
    assert plan[0] == "phase00_schema_bootstrap"
    
    # Should start from Phase 05 if requested
    plan2 = orch._determine_execution_plan(start_stage="phase05_np_grouping")
    assert plan2[0] == "phase05_np_grouping"
    assert len(plan2) < len(plan)
