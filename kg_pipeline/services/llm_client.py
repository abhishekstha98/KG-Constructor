import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class LLMClient(ABC):
    """Abstract base class for LLM client implementations."""

    @abstractmethod
    def generate_structured(self, prompt: str, schema: Type[T], max_tokens: int = 2000) -> T:
        """
        Generate a structured JSON response corresponding to the given Pydantic schema.
        Implementation should handle retries on bad JSON.
        """
        pass

    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Generate unstructured text.
        """
        pass


class MockLLMClient(LLMClient):
    """
    Mock implementation of LLMClient for testing and architectural validation.
    Returns fake valid data based on the schema requested.
    """
    
    def generate_structured(self, prompt: str, schema: Type[T], max_tokens: int = 2000) -> T:
        # In mock mode, many stages will just bypass this and use custom deterministic heuristics 
        # based on the input text natively in the Stage.
        # If this is called, it returns a generic valid dummy.
        dummy_data: Dict[str, Any] = {}
        for field_name, field_info in schema.model_fields.items():
            if field_info.default and field_info.default != getattr(field_info, 'default_factory', None):
                dummy_data[field_name] = field_info.default
            else:
                dummy_data[field_name] = "mock_value_for_" + field_name
        return schema.model_construct(None, **dummy_data)

    def generate_text(self, prompt: str, max_tokens: int = 2000) -> str:
        return "This is a mock response from the LLM based on prompt: " + prompt[:20] + "..."

class ProviderAgnosticLLMClient(LLMClient):
    """
    A concrete wrapper that handles JSON extraction, Pydantic validation, 
    and retries, wrapping a raw text generation function.
    
    (Stubbed for actual API provider injection in the future)
    """
    def __init__(self, raw_generate_func, max_retries: int = 3):
        self.raw_generate_func = raw_generate_func
        self.max_retries = max_retries

    def _extract_json(self, text: str) -> str:
        # Simple extraction of JSON code block if LLM added markdown.
        start = text.find("```json")
        if start != -1:
            end = text.rfind("```")
            if end > start:
                return text[start+7:end].strip()
        
        start = text.find("```")
        if start != -1:
            end = text.rfind("```")
            if end > start:
                return text[start+3:end].strip()
        
        return text.strip()

    def generate_structured(self, prompt: str, schema: Type[T], max_tokens: int = 2000) -> T:
        schema_json = schema.model_json_schema()
        system_instruction = (
            f"You are a strict data extraction system. You must return ONLY valid JSON.\n"
            f"Do not include any markdown formatting, conversational text, or explanations.\n"
            f"Your output MUST precisely match this JSON schema:\n{json.dumps(schema_json, indent=2)}"
        )
        
        full_prompt = f"{system_instruction}\n\nTask Instructions:\n{prompt}"
        
        for attempt in range(self.max_retries):
            try:
                raw_response = self.raw_generate_func(full_prompt, max_tokens)
                json_str = self._extract_json(raw_response)
                data = json.loads(json_str)
                validated = schema.model_validate(data)
                return validated
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode failed on attempt {attempt+1}: {str(e)}")
                full_prompt += f"\n\nERROR: The previous response was not valid JSON ({str(e)}). Please return ONLY raw valid JSON."
            except ValidationError as e:
                logger.warning(f"Schema validation failed on attempt {attempt+1}: {str(e)}")
                full_prompt += f"\n\nERROR: The previous response failed schema validation:\n{str(e)}\nFix the errors and return ONLY raw valid JSON matching the schema."
            except Exception as e:
                logger.error(f"Unexpected error in LLM call: {str(e)}")
                raise
                
        raise ValueError(f"Failed to generate valid structured data matching schema {schema.__name__} after {self.max_retries} attempts.")

    def generate_text(self, prompt: str, max_tokens: int = 2000) -> str:
        return self.raw_generate_func(prompt, max_tokens)
