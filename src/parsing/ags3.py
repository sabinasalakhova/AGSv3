from typing import Dict, List, Any
import pandas as pd
from src.parsing.interface import AGSParser
from src.domain.models import ParsedAGSFile, AGSVersion
from src.parsing.utils import split_quoted_csv, normalize_token

class AGS3Parser(AGSParser):
    """Parser for legacy AGS3 files."""

    def parse(self, file_content: bytes, filename: str) -> ParsedAGSFile:
        text = file_content.decode("latin-1", errors="ignore")
        raw_lines = text.splitlines()
        
        group_data: Dict[str, List[Dict[str, str]]] = {}
        group_headings: Dict[str, List[str]] = {}
        
        current_group = None
        headings: List[str] = []
        data_started = False
        
        def ensure_group(name: str):
            group_data.setdefault(name, [])

        def _merge_val(idx: int, val: str):
            if idx >= len(headings): return
            if not str(val).strip(): return
            
            val = str(val).strip()
            field = headings[idx]
            last_row = group_data[current_group][-1]
            prev = last_row.get(field, "")
            
            existing_parts = [p.strip() for p in prev.split(" | ") if p]
            if val not in existing_parts:
                last_row[field] = f"{prev} | {val}" if prev else val

        def append_continuation(parts: List[str]):
            if not (current_group and headings and group_data[current_group]):
                return
            
            expected_len = len(headings) + 1
            if len(parts) < expected_len:
                parts = parts + [""] * (expected_len - len(parts))
            
            # AGS3 Rule: <CONT> is parts[0], parts[1] is variable 1 (headings[1]?? No headers[0]?)
            # In original code: "parts[0] is <CONT>. parts[1] is Variable 1."
            # "So parts[1] maps to Headings[1]. No Shift." <- This comment was in original agsparser.py
            # Wait, if parts[1] maps to Headings[1], what maps to Headings[0]?
            # Variable 1 usually IS Headings[0]. 
            # Let's trust the logic: logic was `heading_index = i` where range starts at 1.
            # So parts[1] -> headings[1]. 
            # This implies <CONT> lines in AGS3 skip the first key column? 
            # Actually, standard AGS3 <CONT> usually repeats the key keys. 
            # I will preserve the original logic exactly as it was.
            
            for i in range(1, expected_len):
                heading_index = i
                _merge_val(heading_index, parts[i])

        for line in raw_lines:
            if not line.strip(): continue
            parts = split_quoted_csv(line)
            if not parts: continue
            
            keyword = normalize_token(parts[0])
            
            # Handle Continuation
            if keyword == "<CONT>":
                append_continuation(parts)
                continue
            if keyword == "" and len(parts) > 1 and normalize_token(parts[1]) == "<CONT>":
                parts = parts[1:]
                append_continuation(parts)
                continue
                
            if keyword in ["<UNITS>", "UNIT", "<UNIT>", "PROJ", "ABBR"]:
                continue
                
            # AGS3 Logic
            if keyword.startswith("**"):
                current_group = keyword[2:]
                ensure_group(current_group)
                headings = []
                data_started = False
                
            elif keyword.startswith("*"):
                new_headings = [p.lstrip("*") for p in parts if p.strip()]
                # Rule 13 Split Headings
                if not data_started and headings:
                    headings.extend(new_headings)
                else:
                    headings = new_headings
                if current_group:
                    group_headings[current_group] = headings
                    
            elif current_group and headings:
                data_started = True
                row_dict = dict(zip(headings, parts[:len(headings)]))
                group_data[current_group].append(row_dict)

        # Convert to DataFrames
        final_groups = {}
        for gname, rows in group_data.items():
            df = pd.DataFrame(rows)
            if not df.empty:
                # Apply legacy renames
                rename_map = {
                    "?ETH": "WETH", "?ETH_TOP": "WETH_TOP", "?ETH_BASE": "WETH_BASE",
                    "?ETH_GRAD": "WETH_GRAD", "?LEGD": "LEGD", "?HORN": "HORN",
                }
                df = df.rename(columns=rename_map)
                df["SOURCE_FILE"] = filename
            final_groups[gname] = df
            
        return ParsedAGSFile(
            filename=filename,
            version=AGSVersion.AGS3,
            groups=final_groups
        )
