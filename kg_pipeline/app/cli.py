import argparse
import sys
import os
import logging
from uuid import uuid4
from datetime import datetime

# Import stages to auto-register them
from ..stages import *
from ..app.config import settings
from ..pipeline.orchestrator import PipelineOrchestrator
from ..services.artifact_store import ArtifactStore
from ..storage.json_store import JsonStore
from ..domain.models.artifacts import ArtifactEnvelope

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Automated Knowledge Graph Construction Pipeline")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # run command
    run_parser = subparsers.add_parser("run", help="Run the full pipeline on a document or directory")
    run_parser.add_argument("--input", required=True, help="Path to input text file or directory")
    
    # run-stage command
    run_stage_parser = subparsers.add_parser("run-stage", help="Run a specific stage on an existing artifact")
    run_stage_parser.add_argument("--run-id", required=True)
    run_stage_parser.add_argument("--doc-id", required=True)
    run_stage_parser.add_argument("--stage", required=True)
    
    # resume command
    resume_parser = subparsers.add_parser("resume", help="Resume pipeline from a specific stage onward")
    resume_parser.add_argument("--run-id", required=True)
    resume_parser.add_argument("--doc-id", required=True)
    resume_parser.add_argument("--from-stage", required=True)

    args = parser.parse_args()
    
    file_store = JsonStore()
    artifact_store = ArtifactStore(file_store, settings.output_dir)
    orchestrator = PipelineOrchestrator(artifact_store)

    if args.command == "run":
        if os.path.isdir(args.input):
            files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.endswith('.txt')]
        else:
            files = [args.input]

        if not files:
            print(f"No .txt files found to process in {args.input}")
            return

        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for file_path in files:
            doc_id = os.path.basename(file_path).split('.')[0]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Phase 00 input
            initial_artifact = ArtifactEnvelope(
                pipeline_run_id=run_id,
                document_id=doc_id,
                stage_name="init",
                payload={"text": content} # Phase 01 will pick this up if we adjust it
            )
            
            print(f"\\n>>> Processing Document: {doc_id} (Run ID: {run_id})")
            try:
                final_artifact = orchestrator.run_pipeline(run_id, initial_artifact)
                print(f"Success! Final artifact created at phase: {final_artifact.stage_name}")
                if 'export_paths' in final_artifact.payload:
                    print(f"Exported to: {final_artifact.payload['export_paths']}")
            except Exception as e:
                print(f"CRITICAL FAILURE on doc {doc_id}: {str(e)}")

    elif args.command == "run-stage" or args.command == "resume":
        print(f"Command '{args.command}' is scaffolded for architectural completeness. \\n"
              f"In a stateful system, this would load the ArtifactEnvelope for run {args.run_id} "
              f"from the ArtifactStore and trigger the Orchestrator starting at {args.stage if args.command == 'run-stage' else args.from_stage}.")

if __name__ == "__main__":
    main()
