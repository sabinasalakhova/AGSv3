import csv
import io
from typing import List, Dict

def split_quoted_csv(line: str) -> List[str]:
    """
    Parses a single CSV line using the standard csv library.
    """
    if not line or not line.strip():
        return []
    try:
        reader = csv.reader(io.StringIO(line.strip()), strict=False, skipinitialspace=True)
        return next(reader)
    except Exception:
        return []

def normalize_token(token: str) -> str:
    if token is None:
        return ""
    return token.strip().strip('"').lstrip("\ufeff").upper()

def detect_ags_version(file_bytes: bytes) -> str:
    """
    Quickly scans the file to determine AGS version.
    Returns "AGS3", "AGS4", or "UNKNOWN".
    """
    try:
        content = file_bytes.decode("latin-1", errors="ignore")
        lines = content.splitlines()[:50]
        for line in lines:
            s = line.strip()
            if not s: continue
            
            # Check for AGS4 GROUP tag
            if s.startswith('"GROUP"') or s.startswith("GROUP"):
                return "AGS4"
            # Check for AGS3 ** tag
            if s.startswith('"**') or s.startswith("**"):
                return "AGS3"
    except Exception:
        pass
    return "UNKNOWN"
