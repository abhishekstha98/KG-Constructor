from enum import Enum, auto

class strEnum(str, Enum):
    pass

class StageName(strEnum):
    PHASE00_SCHEMA_BOOTSTRAP = "phase00_schema_bootstrap"
    PHASE01_DOCUMENT_NORMALIZATION = "phase01_document_normalization"
    PHASE02_SENTENCE_PREPARATION = "phase02_sentence_preparation"
    PHASE03_ENTITY_EXTRACTION = "phase03_entity_extraction"
    PHASE04_ENTITY_CANONICALIZATION = "phase04_entity_canonicalization"
    PHASE05_NP_GROUPING = "phase05_np_grouping"
    PHASE06_RELATION_EXTRACTION = "phase06_relation_extraction"
    PHASE07_SRL = "phase07_srl"
    PHASE08_ROLE_ALIGNMENT = "phase08_role_alignment"
    PHASE09_PREDICATE_MAPPING = "phase09_predicate_mapping"
    PHASE10_RDF_GENERATION = "phase10_rdf_generation"
    PHASE11_VALIDATION_REPAIR = "phase11_validation_repair"
    PHASE12_EXPORT = "phase12_export"

class EntityType(strEnum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    EVENT = "EVENT"
    CONCEPT = "CONCEPT"
    OTHER = "OTHER"

class RoleType(strEnum):
    AGENT = "AGENT"
    PATIENT = "PATIENT"
    THEME = "THEME"
    INSTRUMENT = "INSTRUMENT"
    LOCATION = "LOCATION"
    TIME = "TIME"
    OTHER = "OTHER"

class PredicateMappingSource(strEnum):
    WIKIDATA = "WIKIDATA"
    SCHEMA_ORG = "SCHEMA_ORG"
    CUSTOM = "CUSTOM"
    LLM_DERIVED = "LLM_DERIVED"

class ValidationStatus(strEnum):
    PENDING = "PENDING"
    VALID = "VALID"
    WARNING = "WARNING"
    INVALID = "INVALID"
    REPAIRED = "REPAIRED"

class ObjectTypeLiteralVsIri(strEnum):
    LITERAL = "LITERAL"
    IRI = "IRI"

class SourceDocumentType(strEnum):
    TEXT = "TEXT"
    PDF_EXTRACT = "PDF_EXTRACT"
    HTML = "HTML"
    JSON = "JSON"
    OTHER = "OTHER"
