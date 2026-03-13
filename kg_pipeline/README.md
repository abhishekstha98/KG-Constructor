# KG Pipeline Foundation

A production-grade, staged automated knowledge graph construction pipeline.

## Architecture Guidelines

- **Pydantic Driven**: All artifacts between stages are strongly typed Python objects serialized to JSON.
- **Stateless Stages**: Each phase (00 through 12) takes an `ArtifactEnvelope` and returns a new version of the envelope. It does not carry hidden in-memory state.
- **Provenance**: Every output contains a robust provenance log.
- **Fail Loudly**: Schema violations should halt the pipeline explicitly to prevent cascading bad data.

## How to Run the Demo

The pipeline is set up with a deterministic mock mode that allows you to see the architecture in action without requiring an LLM API key.

### 1. Install dependencies
Ensure you have `pydantic` and `pydantic-settings` installed.

### 2. Run the pipeline
Execute the full pipeline on the sample input text:
```bash
python -m kg_pipeline.app.cli run --input kg_pipeline/data/input/sample.txt
```

### 3. Inspect Outputs
- **Intermediate Artifacts**: Check `data/output/<run_id>/<doc_id>/` for the detailed JSON envelopes produced by each individual stage.
- **Final Export**: Check `data/output/final_exports/<doc_id>/graph.nt` for the generated N-Triples RDF file.

## Execution Modes

1. **Mock Mode (Default)**: Uses heuristic logic in each stage. Controlled by `KG_LLM_MOCK_MODE=True` (default in `config.py`).
2. **LLM Mode**: To enable LLM integration, set `KG_LLM_MOCK_MODE=False` and inject a concrete `generate_text` function into the `ProviderAgnosticLLMClient`. The stages will then use the prompt files located in `prompts/`.
