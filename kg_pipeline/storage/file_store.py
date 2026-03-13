from abc import ABC, abstractmethod
from typing import Any, Optional

class FileStore(ABC):
    """Abstract interface for reading and writing data to storage."""
    
    @abstractmethod
    def read(self, path: str) -> Optional[Any]:
        """Read data from the given path."""
        pass

    @abstractmethod
    def write(self, path: str, data: Any):
        """Write data to the given path."""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a path exists in storage."""
        pass
