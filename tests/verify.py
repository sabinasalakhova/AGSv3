import sys
import os

# Add root to path so we can import src
sys.path.append(os.getcwd())

from src.parsing import get_parser
from src.parsing.utils import detect_ags_version

def test_parsing():
    file_path = "ags_data/33597-1605.AGS"
    print(f"Testing file: {file_path}")
    
    with open(file_path, "rb") as f:
        content = f.read()
        
    version = detect_ags_version(content)
    print(f"Detected Version: {version}")
    
    parser = get_parser(version)
    parsed_file = parser.parse(content, file_path)
    
    if parsed_file.is_valid:
        print("Parsing Successful!")
        print(f"Found {len(parsed_file.groups)} groups:")
        for gname in parsed_file.groups:
            print(f" - {gname} ({len(parsed_file.groups[gname])} rows)")
    else:
        print("Parsing Failed!")
        for error in parsed_file.errors:
            print(f"[Error] Line {error.line}: {error.message}")

if __name__ == "__main__":
    test_parsing()
