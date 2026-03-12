from typing import Any, Protocol

class ExtractionInterface(Protocol):
    def extract(self, file_path: str) -> Any:
        """Extract data from the given file path."""
        pass