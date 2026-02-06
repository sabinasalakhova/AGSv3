from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, List
import pandas as pd

class AGSVersion(Enum):
    AGS3 = "AGS3"
    AGS4 = "AGS4"
    UNKNOWN = "UNKNOWN"

@dataclass
class AGS4Error:
    """Represents an error found during AGS4 validation."""
    rule: str
    line: int
    message: str

@dataclass
class ParsedAGSFile:
    """Result of parsing an AGS file."""
    filename: str
    version: AGSVersion
    groups: Dict[str, pd.DataFrame] = field(default_factory=dict)
    errors: List[AGS4Error] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
