import json
from kg_pipeline.domain.models.artifacts import ArtifactEnvelope
from kg_pipeline.domain.models.common import ConfidenceSummary

def test_artifact_envelope_serialization():
    art = ArtifactEnvelope(
        pipeline_run_id="run_1",
        document_id="doc_1",
        stage_name="test_stage",
        payload={"key": "value"},
        confidence_summary=ConfidenceSummary(overall_score=0.95)
    )
    
    js = art.model_dump_json()
    assert "run_1" in js
    assert "doc_1" in js
    assert "test_stage" in js
    assert "0.95" in js
    
    reloaded = ArtifactEnvelope.model_validate_json(js)
    assert reloaded.pipeline_run_id == "run_1"
    assert reloaded.payload == {"key": "value"}
