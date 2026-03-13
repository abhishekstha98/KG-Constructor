import hashlib
import re

class URIMinter:
    """
    Generates deterministic, stable URIs for various domain entities.
    Uses SHA-256 hashing where needed to ensure id-to-uri stability.
    """
    
    def __init__(self, base_namespace: str):
        self.base_namespace = base_namespace.rstrip('/') + '/'

    def _slugify(self, text: str) -> str:
        # Convert to snake_case and remove special chars for cleaner URIs
        s = text.lower()
        s = re.sub(r'[^a-z0-9]+', '_', s)
        return s.strip('_')

    def mint_entity_uri(self, canonical_name: str, entity_type: str) -> str:
        """Create a stable URI for an entity."""
        slug = self._slugify(canonical_name)
        return f"{self.base_namespace}entity/{entity_type}/{slug}"

    def mint_predicate_uri(self, predicate_text: str) -> str:
        """Create a stable URI for a predicate if no ontology mapping exists."""
        slug = self._slugify(predicate_text)
        return f"{self.base_namespace}predicate/{slug}"

    def mint_sentence_id(self, doc_id: str, sentence_index: int) -> str:
        """Create a structured ID for a sentence."""
        return f"{doc_id}#s{sentence_index}"
