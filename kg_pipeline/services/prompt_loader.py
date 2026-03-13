import os
from string import Template
from typing import Dict, Any

class PromptLoader:
    """Loads and templates prompts from text files."""
    
    def __init__(self, prompts_dir: str):
        self.prompts_dir = prompts_dir

    def load_prompt(self, stage_name_val: str, variables: Dict[str, Any]) -> str:
        """
        Loads a prompt template for a specific stage and substitutes variables.
        """
        filename = f"{stage_name_val}.txt"
        path = os.path.join(self.prompts_dir, filename)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            template_str = f.read()
            
        template = Template(template_str)
        return template.safe_substitute(variables)
