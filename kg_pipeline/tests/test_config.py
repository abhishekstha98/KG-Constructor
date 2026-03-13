from kg_pipeline.app.config import PipelineConfig

def test_config_defaults():
    config = PipelineConfig()
    assert config.project_name == "Automated OIE KG Pipeline"
    assert config.max_retries == 3
    assert "entity" in config.confidence_thresholds
    assert len(config.enabled_stages) > 0
