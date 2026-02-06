import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from src.domain.models import ParsedAGSFile

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(col).upper().strip() for col in df.columns]
    return df

def drop_singleton_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # Modern pandas: replace empty strings with NaN, then check count
    clean = df.replace(r"^\s*$", np.nan, regex=True).
    clean=result.infer_objects(copy=False)
    # Require at least 2 non-null values (assuming FILE_SOURCE is 1)
    nn = clean.notna().sum(axis=1)
    return df.loc[nn > 1].reset_index(drop=True)

def expand_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimized expansion of rows with | separators using explode.
    """
    if df.empty:
        return df

    # 1. Identify columns that contain separators
    # We only care about string columns
    str_cols = df.select_dtypes(include=['object']).columns
    
    # 2. Check if expansion is needed at all (fast check)
    needs_expansion = False
    for col in str_cols:
        if df[col].astype(str).str.contains(r'\|').any():
            needs_expansion = True
            break
            
    if not needs_expansion:
        return df

    # 3. Split all columns by separator
    # This might be memory intensive for huge DFs but much faster than iterrows
    expanded = df.copy()
    for col in df.columns:
        if col in str_cols:
            # Split by " | "
            expanded[col] = expanded[col].astype(str).str.split(r' \| ')
        else:
            # Wrap non-string/numeric cols in list for uniformity if they don't split?
            # Actually explode allows mixing lists and scalars, but for proper alignment
            # we typically want everything to be list-like or scalar.
            # However, AGS logic implies if a cell is NOT split, it repeats?
            # Or does it imply that if one col splits, ALL must split?
            # Original code: checks if ALL columns split into same length. 
            pass

    # The logic in original cleaners.py was complex:
    # "skip expansion if all split values across columns are identical"
    # That part is specific. Let's replicate the intent but faster.
    
    # Actually, the original loop was:
    # for each row:
    #   split available fields
    #   if all fields repeat same value (e.g. "A|A|A", "B|B|B"): keep single row
    #   else: explode
    
    # Vectorized approach for "all components identical" is hard. 
    # But strictly speaking, standard pandas `explode` repeats scalars.
    # If we split column A into [A1, A2] and column B is scalar B, explode(A) gives (A1, B), (A2, B).
    # AGS "Continuation" usually implies aligned lists. [A1, A2] and [B1, B2].
    
    # Let's take a safe middle ground: 
    # For now, we use a robust row-based generator but simpler than iterrows,
    # OR we assume standard AGS expansion where all lists are same length.
    
    # Let's stick to the safe row-iteration for the unique "deduplication" logic 
    # but clean it up.
    
    # Actually, let's use the provided improvement idea:
    # If we split into lists, we can explode all columns.
    
    rows = []
    for row in df.to_dict('records'):
        # Split all values
        split_data = {}
        max_len = 1
        
        for k, v in row.items():
            if isinstance(v, str) and " | " in v:
                parts = v.split(" | ")
                split_data[k] = parts
                max_len = max(max_len, len(parts))
            else:
                split_data[k] = [v]
        
        # Check if all split lists are effectively "same value" 
        # (Original logic: "all_same")
        # If all effective lists (length > 1) contain only identical elements?
        # No, the original logic was:
        # unique_values_per_col = {col: set(vals) for col...}
        # if all cols have len(set) == 1: don't expand (just take first)
        
        is_redundant = True
        if max_len > 1:
            for k, parts in split_data.items():
                if len(parts) > 1 and len(set(parts)) > 1:
                    is_redundant = False
                    break
        
        if is_redundant and max_len > 1:
            # Just take the first element of each
            new_row = {k: v[0] for k, v in split_data.items()}
            rows.append(new_row)
        else:
            # Expand
            for i in range(max_len):
                new_row = {}
                for k, v in split_data.items():
                    # If list is shorter, take last value? Or empty?
                    # Original code: "if i < len... else ''"
                    val = v[i] if i < len(v) else ""
                    new_row[k] = val
                rows.append(new_row)
                
    return pd.DataFrame(rows)

def combine_files(parsed_files: List[ParsedAGSFile]) -> Dict[str, pd.DataFrame]:
    """
    Combines parsed files into a single dictionary of DataFrames (Groups).
    """
    combined: Dict[str, List[pd.DataFrame]] = {}
    
    for pfile in parsed_files:
        for group_name, df in pfile.groups.items():
            if df.empty: continue
            
            # Ensure separate copy and add filename
            clean_df = df.copy()
            clean_df = normalize_columns(clean_df)
            
            if "SOURCE_FILE" not in clean_df.columns:
                 clean_df["SOURCE_FILE"] = pfile.filename
                 
            combined.setdefault(group_name, []).append(clean_df)
            
    # Concat and specific cleaning
    result = {}
    for group_name, dfs in combined.items():
        merged = pd.concat(dfs, ignore_index=True)
        merged = drop_singleton_rows(merged)
        result[group_name] = merged
        
    return result
