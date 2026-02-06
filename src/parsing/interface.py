from typing import Protocol, List, Dict
import pandas as pd
from src.domain.models import ParsedAGSFile

class AGSParser(Protocol):
    """Interface for AGS file parsers."""

    def parse(self, file_content: bytes, filename: str) -> ParsedAGSFile:
        """Parses the AGS file content and returns a ParsedAGSFile object."""
        ...
