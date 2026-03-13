from kg_pipeline.pipeline.registry import StageRegistry
from kg_pipeline.domain.enums import StageName

def test_registry_contains_core_stages():
    # We must import the stages module to trigger registration
    import kg_pipeline.stages
    
    stages = StageRegistry.get_registered_stages()
    assert StageName.PHASE00_SCHEMA_BOOTSTRAP in stages
    assert StageName.PHASE12_EXPORT in stages

def test_resolve_stage():
    import kg_pipeline.stages
    
    cls = StageRegistry.resolve_stage(StageName.PHASE01_DOCUMENT_NORMALIZATION)
    assert cls.__name__ == "Phase01DocumentNormalization"
    
    instance = cls()
    assert instance.phase_name == StageName.PHASE01_DOCUMENT_NORMALIZATION
