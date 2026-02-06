from typing import Dict, List
import pandas as pd
from python_ags4 import AGS4
from src.parsing.interface import AGSParser
from src.domain.models import ParsedAGSFile, AGSVersion, AGS4Error

class AGS4Parser(AGSParser):
    """Parser for AGS4 files using the official python-ags4 library."""

    def parse(self, file_content: bytes, filename: str) -> ParsedAGSFile:
        # python-ags4 expects a file-like object or path
        # It handles encoding internally, but usually expects utf-8 or cp1252
        # We'll pass a StringIO or BytesIO if supported. 
        # AGS4.AGS4_to_dataframe takes "filepath_or_buffer".
        
        # We need to decode first because AGS4_to_dataframe might expect text if passing a StringIO,
        # or it handles bytes if we pass BytesIO? 
        # Looking at AGS4.py: `if _is_file_like(filepath_or_buffer):` ...
        # It seems safer to decode to string and pass StringIO to ensure encoding control.
        
        try:
            text_content = file_content.decode("utf-8")
        except UnicodeDecodeError:
            text_content = file_content.decode("latin-1", errors="replace")
            
        from io import StringIO
        f = StringIO(text_content)
        
        try:
            # get_line_numbers=False, rename_duplicate_headers=True
            tables, headings = AGS4.AGS4_to_dataframe(f)
            
            # Convert to our structure
            # AGS4 lib returns Dict[str, DataFrame]
            
            for key in tables:
                tables[key]["SOURCE_FILE"] = filename
                
            return ParsedAGSFile(
                filename=filename,
                version=AGSVersion.AGS4,
                groups=tables
            )
            
        except Exception as e:
            # If standard parser fails, we return an error state
            return ParsedAGSFile(
                filename=filename,
                version=AGSVersion.AGS4,
                errors=[AGS4Error(rule="Parser", line=0, message=str(e))]
            )
