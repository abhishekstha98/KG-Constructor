import json
import os
from typing import Any, Optional
from .file_store import FileStore

class JsonStore(FileStore):
    """Concrete implementation of FileStore using JSON files on disk."""
    
    def read(self, path: str) -> Optional[Any]:
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def write(self, path: str, data: Any):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def exists(self, path: str) -> bool:
        return os.path.exists(path)
