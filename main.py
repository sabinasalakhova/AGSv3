import streamlit as st
import pandas as pd
import re
from typing import List, Tuple, Dict
from io import BytesIO
from python_ags4 import AGS4

from agsparser import (
    analyze_ags_content,
    parse_ags_file,
    find_hole_id_column
)
from cleaners import combine_groups   
# ────────────────────────────────────────────────
#STREAMLIT PAGE CONFIGURATION
# ────────────────────────────────────────────────

st.set_page_config(page_title="AGS File Processor", layout="wide")

st.title("AGS File Processor")
st.divider()
st.write("Upload AGS3 or AGS4 files for processing")

# ────────────────────────────────────────────────
# Version Choice
# ────────────────────────────────────────────────
st.subheader("Select AGS version mode")
mode = st.radio(
    "Choose version (prevents mixing AGS3 and AGS4)",
    options=["AGS3 (legacy)", "AGS4 (modern)"],
    horizontal=True,
    index=1
)

is_ags3_mode = "AGS3" in mode
is_ags4_mode = "AGS4" in mode

if is_ags3_mode:
    st.info("Only legacy AGS3 files (**GROUP style) will be accepted.")
else:
    st.info("Only AGS4 files (GROUP, HEADING, DATA style) will be accepted.")
    

# ────────────────────────────────────────────────
# UPLOAD BUTTONS FOR AGS FILES 
# 2 OPTIONS/VARIABLES: files_no_prefix, files_with_prefix
# ────────────────────────────────────────────────
st.subheader("Upload files")

file_types = ["ags", "txt", "ags4"]

col1, col2 = st.columns(2)

with col1:
    st.subheader("No prefix")
    st.caption("Original HOLE_ID / LOCA_ID")
    files_no_prefix = st.file_uploader(
    "Upload files (no prefix)",
    type=file_types,
    accept_multiple_files=True,
    key="no_prefix" )


with col2:
    st.subheader("With prefix")
    st.caption("Prefix = first 5 chars of filename + '_'")
    files_with_prefix = st.file_uploader(
        "Upload files (with prefix)",
        type=file_types,
        accept_multiple_files=True,
        key="with_prefix"
    )

# ────────────────────────────────────────────────
# creates a *list* containing *tuples (file,bool)* :  all_uploaded = [(file1, False), (file2, True), ...]
# where False - no need for prefix, True - needs prefix
# shows how many files were uploaded
# ────────────────────────────────────────────────

all_uploaded = []

if files_no_prefix:
    all_uploaded.extend([(f, False) for f in files_no_prefix])
    
if files_with_prefix:
    all_uploaded.extend([(f, True) for f in files_with_prefix])

if not all_uploaded:
    st.info("Upload at least one file in one or both sections.")
    st.stop()

st.success(f"**{len(all_uploaded)} file(s)** ready for processing in **{mode}** mode")

# ────────────────────────────────────────────────
# Processing with progress & warnings
# ────────────────────────────────────────────────
all_group_dfs: List[Tuple[str, Dict[str, pd.DataFrame]]] = []   #expected structure for later combine_ags.py use
diagnostics = []
failed_files = []

#progress visulization for streamlit 

progress_bar = st.progress(0)
status = st.empty()

with st.status("Processing files…", expanded=True) as proc_status:
    for idx, (file_obj, needs_prefix) in enumerate(all_uploaded, 1):
        fname = file_obj.name
        status.text(f"[{idx}/{len(all_uploaded)}] Checking {fname}")

        try:
            file_bytes = file_obj.getvalue()

            # Version validation
            flags = analyze_ags_content(file_bytes)
            is_ags3 = flags.get("AGS3") == "Yes"
            is_ags4 = flags.get("AGS4") == "Yes"

            if is_ags3_mode and not is_ags3:
                raise ValueError("File detected as AGS4/unknown — mode is AGS3. Change Mode to AGS4.")
            if is_ags4_mode and not is_ags4:
                raise ValueError("File detected as AGS3/unknown — mode is AGS4. Change Mode to AGS3.")

            diagnostics.append((fname, flags))

            # Prefix
            prefix = ""
            if needs_prefix:
                base = fname.split('.')[0].upper()
                prefix = re.sub(r'[^A-Z0-9]', '', base)[:5] + "_"
                status.text(f"[{idx}/{len(all_uploaded)}] {fname} → prefix '{prefix}'")

            # Parse
            status.text(f"[{idx}/{len(all_uploaded)}] Parsing {fname}")
            groups = parse_ags_file(file_bytes, fname)

            if not groups:
                raise ValueError("No valid groups parsed.")

            # Apply prefix
            if prefix:
                status.text(f"[{idx}/{len(all_uploaded)}] Applying prefix to {fname}")
                for gname, df in groups.items():
                    loc_col = find_hole_id_column(df.columns)
                    if loc_col:
                        df[loc_col] = prefix + df[loc_col].astype(str).str.strip()

            all_group_dfs.append((fname, groups))

            status.text(f"[{idx}/{len(all_uploaded)}] Success: {fname}")

        except Exception as e:
            failed_files.append((fname, str(e)))
            status.text(f"[{idx}/{len(all_uploaded)}] FAILED: {fname} — {str(e)}")
            st.warning(f"Skipped {fname}: {str(e)}")

        progress_bar.progress(idx / len(all_uploaded))

    proc_status.update(label="All files processed", state="complete")

# ────────────────────────────────────────────────
# Final warnings & results
# ────────────────────────────────────────────────
if failed_files:
    st.error(f"**{len(failed_files)} file(s) failed**")
    st.dataframe(pd.DataFrame(failed_files, columns=["File", "Reason"]))

if not all_group_dfs:
    st.warning("No files were successfully parsed. Check mode/version match.")
    st.stop()

# ─── Use the existing combiner from cleaners.py ───
status.text("Combining groups across files...")
combined_groups = combine_groups(all_group_dfs)
status.text("Combining complete.")

st.success(f"**Combined {len(all_group_dfs)} file(s)** → **{len(combined_groups)} groups**")

# Diagnostics
with st.expander("File diagnostics", expanded=False):
    diag_df = pd.DataFrame([{"File": n, **f} for n, f in diagnostics])
    st.dataframe(diag_df, width='stretch')

# Results
st.subheader("View combined data")
group_list = sorted(combined_groups.keys())
selected = st.selectbox("Select group:", group_list)

if selected:
    df = combined_groups[selected]
    st.subheader(f"{selected} – {len(df):,} rows × {len(df.columns)} columns")

    if len(df) > 50000:
        st.warning("Large table (>50k rows) — showing first 1,000 rows only.")

    st.dataframe(df.head(1000), width='stretch')

    # Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download combined group as CSV",
        csv,
        f"combined_{selected}.csv",
        "text/csv"
    )



