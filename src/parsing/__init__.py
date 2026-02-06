from src.parsing.interface import AGSParser
from src.parsing.ags3 import AGS3Parser
from src.parsing.ags4 import AGS4Parser
from src.parsing.utils import detect_ags_version
from src.domain.models import AGSVersion

def get_parser(version: str) -> AGSParser:
    if version == "AGS3":
        return AGS3Parser()
    elif version == "AGS4":
        return AGS4Parser()
    return AGS4Parser() 
