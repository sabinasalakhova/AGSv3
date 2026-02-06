import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from src.domain.models import ParsedAGSFile
import io


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(col).upper().strip() for col in df.columns]
    return df

def drop_singleton_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # Modern pandas: replace empty strings with NaN, then check count
    clean = df.replace(r"^\s*$", np.nan, regex=True).infer_objects(copy=False)
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

def create_excel_from_dict(data_dict: Dict[str, pd.DataFrame], filename: str = "workbook.xlsx") -> bytes:
    """Excel builder - takes any dict of DataFrames and returns Excel bytes."""
    with io.BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            for sheet_name, df in data_dict.items():
                if not df.empty:
                    # Clean sheet name (Excel limits), double checking even though the most common variants have been renamed before, if another name pops up it will change it to _
                    clean_name = str(sheet_name)[:31].replace('/', '_').replace('\\', '_')
                    df.to_excel(writer, sheet_name=clean_name, index=False)
        return buffer.getvalue()

def build_key_data_excel_options(key_data_groups: Dict[str, pd.DataFrame]) -> Dict[str, bytes]:
    
    """Main entry point for extracting key data"""
    
    if not key_data_groups:
        return {}
    
    options = {}
    
    # Option 1: Mapped intervals
    mapped_df = get_key_data_intervals_mapped(key_data_groups)
    if not mapped_df.empty:
        options["Mapped Intervals"] = create_excel_from_dict(
            {"Mapped_Intervals": mapped_df}, "intervals_mapped.xlsx"
        )
    
    # Option 2: Full intervals
    full_df = get_key_data_intervals_full(key_data_groups)
    if not full_df.empty:
        options["Full Intervals"] = create_excel_from_dict(
            {"Full_Intervals": full_df}, "intervals_full.xlsx"
        )
    
 
    
    return options

def get_key_data_groups(combined_groups: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Extract key data groups: CORE, WETH, GEOL, FRAC, DETL, SAMP
    """
    key_groups = ["CORE", "WETH", "GEOL", "FRAC", "DETL", "SAMP"]
    key_data = {}
    
    for group_name in key_groups:
        if group_name in combined_groups:
            key_data[group_name] = combined_groups[group_name]
    
    return key_data


def get_key_data_intervals_mapped(key_data_groups: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    VERSION 1: Mapped Columns ("Like Before")
    Combine key data groups into depth intervals with SPECIFIC, clean column names.
    Includes robust type conversion.
    """
    if not key_data_groups:
        return pd.DataFrame()
    
    # Configuration with specific mappings (Source Column -> Output Column) this is from legacy code
    group_configs = {
        'CORE': ('CORE_TOP', 'CORE_BOT', {'CORE_RQD': 'RQD', 'CORE_PREC': 'TCR'}),
        'DETL': ('DETL_TOP', 'DETL_BASE', {'DETL_DESC': 'Details'}),
        'FRAC': ('FRAC_TOP', 'FRAC_BASE', {'FRAC_FI': 'FI'}),
        'GEOL': ('GEOL_TOP', 'GEOL_BASE', {'GEOL_LEG': 'GEOL', 'GEOL_DESC': 'GEOL_DESC'}),
        'WETH': ('WETH_TOP', 'WETH_BASE', {'WETH_GRAD': 'WETH_GRAD'}),
        'SAMP': ('SAMP_TOP', 'SAMP_BASE', {'SAMP_TYPE': 'SAMP_TYPE', 'SAMP_ID': 'SAMP_ID'})
    }

    # 1. Prepare simple depth keys for the helper
    simple_depth_keys = {g: (cfg[0], cfg[1]) for g, cfg in group_configs.items()}
    
    # 2. Use Helper to get Master Intervals
    result_df = _calculate_master_intervals(key_data_groups, simple_depth_keys)

    if result_df.empty:
        return pd.DataFrame()

    # Initialize Mapped Columns
    output_columns = set()
    for _, _, cols in group_configs.values():
        output_columns.update(cols.values())
    for col in output_columns:
        result_df[col] = None

    # 3. Fill Data using Mappings
    for group_name, (top_col, base_col, column_mapping) in group_configs.items():
        if group_name not in key_data_groups: continue
        source_df = key_data_groups[group_name].copy()
        
        if top_col not in source_df.columns or base_col not in source_df.columns: continue
        
        source_df[top_col] = pd.to_numeric(source_df[top_col], errors='coerce')
        source_df[base_col] = pd.to_numeric(source_df[base_col], errors='coerce')
        source_df = source_df.dropna(subset=[top_col, base_col])

        for _, row in source_df.iterrows():
            mask = (
                (result_df['HOLE_ID'] == str(row['HOLE_ID'])) & 
                (result_df['DEPTH_FROM'] >= row[top_col]) & 
                (result_df['DEPTH_FROM'] < row[base_col])
            )
            if mask.any():
                for source_col, target_col in column_mapping.items():
                    if source_col in row.index:
                        result_df.loc[mask, target_col] = row[source_col]

    return result_df.reset_index(drop=True)


def get_key_data_intervals_full(key_data_groups: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    VERSION 2: All Columns )
    Combine key data groups into depth intervals and automatically attach ALL available columns.
    Includes robust type conversion.
    """
    if not key_data_groups:
        return pd.DataFrame()
    
    group_depth_keys = {
        'CORE': ('CORE_TOP', 'CORE_BOT'),
        'DETL': ('DETL_TOP', 'DETL_BASE'),
        'FRAC': ('FRAC_TOP', 'FRAC_BASE'),
        'GEOL': ('GEOL_TOP', 'GEOL_BASE'),
        'WETH': ('WETH_TOP', 'WETH_BASE'),
        'SAMP': ('SAMP_TOP', 'SAMP_BASE')
    }
    
    # 1. Use Helper to get Master Intervals
    result_df = _calculate_master_intervals(key_data_groups, group_depth_keys)

    if result_df.empty:
        return pd.DataFrame()

    # 2. Initialize ALL Columns (Dynamic Discovery)
    structural_cols = {'HOLE_ID', 'SOURCE_FILE', 'GIU_HOLE_ID', 'GIU_NO'}
    for t, b in group_depth_keys.values():
        structural_cols.add(t)
        structural_cols.add(b)

    for group_name in group_depth_keys:
        if group_name in key_data_groups:
            cols = key_data_groups[group_name].columns
            data_cols = [c for c in cols if c not in structural_cols]
            for col in data_cols:
                if col not in result_df.columns:
                    result_df[col] = None

    # 3. Fill Data Dynamically
    for group_name, (top_col, base_col) in group_depth_keys.items():
        if group_name not in key_data_groups: continue
        source_df = key_data_groups[group_name].copy()
        
        if top_col not in source_df.columns or base_col not in source_df.columns: continue
        
        source_df[top_col] = pd.to_numeric(source_df[top_col], errors='coerce')
        source_df[base_col] = pd.to_numeric(source_df[base_col], errors='coerce')
        source_df = source_df.dropna(subset=[top_col, base_col])

        # Identify columns to copy (intersection of source and result, excluding structural)
        valid_cols = [c for c in source_df.columns if c in result_df.columns and c not in structural_cols]
        if not valid_cols: continue

        for _, row in source_df.iterrows():
            mask = (
                (result_df['HOLE_ID'] == str(row['HOLE_ID'])) & 
                (result_df['DEPTH_FROM'] >= row[top_col]) & 
                (result_df['DEPTH_FROM'] < row[base_col])
            )
            if mask.any():
                result_df.loc[mask, valid_cols] = row[valid_cols].values

    return result_df.reset_index(drop=True)

def _calculate_master_intervals(key_data_groups: Dict[str, pd.DataFrame], group_depth_keys: Dict[str, Tuple[str, str]]) -> pd.DataFrame:
    """Helper: Calculates the master depth slices based on provided groups."""
    all_holes = set()
    for df in key_data_groups.values():
        if 'HOLE_ID' in df.columns:
            all_holes.update(df['HOLE_ID'].dropna().astype(str).unique())
            
    hole_intervals = {}
    for hole_id in all_holes:
        all_depths = []
        for group_name, (top_col, base_col) in group_depth_keys.items():
            if group_name not in key_data_groups: continue
            df = key_data_groups[group_name]
            hole_data = df[df['HOLE_ID'].astype(str) == hole_id]
            
            if top_col in hole_data.columns:
                all_depths.extend(pd.to_numeric(hole_data[top_col], errors='coerce').dropna().tolist())
            if base_col in hole_data.columns:
                all_depths.extend(pd.to_numeric(hole_data[base_col], errors='coerce').dropna().tolist())
        
        if all_depths:
            unique_depths = sorted(list(set(all_depths)))
            if len(unique_depths) > 1:
                intervals = []
                for i in range(len(unique_depths) - 1):
                    intervals.append({
                        'HOLE_ID': hole_id,
                        'DEPTH_FROM': unique_depths[i],
                        'DEPTH_TO': unique_depths[i + 1],
                        'THICKNESS_M': unique_depths[i + 1] - unique_depths[i]
                    })
                hole_intervals[hole_id] = intervals
                
    all_rows = []
    for intervals in hole_intervals.values():
        all_rows.extend(intervals)
    return pd.DataFrame(all_rows)

