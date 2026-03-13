import re
from typing import Optional, Type, Any
from pydantic import BaseModel
from ..app.config import settings
from ..domain.enums import StageName
from ..domain.models.artifacts import ArtifactEnvelope
from ..domain.models.documents import Document, Section, Sentence, Clause
from ..services.uri_minter import URIMinter
from ..pipeline.base_stage import BaseStage
from ..pipeline.registry import StageRegistry

@StageRegistry.register(StageName.PHASE02_SENTENCE_PREPARATION)
class Phase02SentencePreparation(BaseStage):
    """
    Phase 02: Sentence Preparation
    Splits the document sections into sentences and clauses for granular processing.
    """

    @property
    def phase_name(self) -> str:
        return StageName.PHASE02_SENTENCE_PREPARATION

    @property
    def expected_input_payload_type(self) -> Optional[Type[BaseModel]]:
        return Document

    @property
    def expected_output_payload_type(self) -> Optional[Type[BaseModel]]:
        return Document

    def execute(self, input_artifact: ArtifactEnvelope) -> Any:
        doc: Document = input_artifact.payload  # type: ignore
        minter = URIMinter(str(settings.base_uri_namespace))
        
        sentence_idx = 0
        for section in doc.sections:
            # Very naive regex sentence splitter
            raw_sentences = re.split(r'(?<=[.!?]) +', section.text)
            char_offset = 0
            
            for rs in raw_sentences:
                trim_rs = rs.strip()
                if not trim_rs:
                    continue
                
                # Simple clause split by commas for mock
                raw_clauses = [c.strip() for c in trim_rs.split(',')]
                clauses = []
                c_offset = 0
                for ci, ctext in enumerate(raw_clauses):
                    if ctext:
                        clauses.append(Clause(
                            clause_id=f"{doc.document_id}_s{sentence_idx}_c{ci}",
                            text=ctext,
                            start_char=c_offset,
                            end_char=c_offset + len(ctext)
                        ))
                    c_offset += len(ctext) + 1 # +1 for comma
                
                sent_id = minter.mint_sentence_id(doc.document_id, sentence_idx)
                section.sentences.append(Sentence(
                    sentence_id=sent_id,
                    text=trim_rs,
                    start_char=char_offset,
                    end_char=char_offset + len(trim_rs),
                    clauses=clauses
                ))
                
                char_offset += len(rs)
                if rs.endswith(' '):
                    char_offset += 1
                sentence_idx += 1
                
        return doc
