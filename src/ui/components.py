import streamlit as st
import pandas as pd
from typing import List, Tuple, Any

def setup_page():
    st.set_page_config(page_title="AGS File Processor", layout="wide")
    st.title("AGS File Processor")
    st.divider()

def display_file_uploaders() -> Tuple[List[Any], List[Any]]:
    st.subheader("Upload files")
    file_types = ["ags", "txt", "ags4"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("No prefix")
        st.caption("Original HOLE_ID / LOCA_ID")
        files_no = st.file_uploader(
            "Upload files (no prefix)",
            type=file_types,
            accept_multiple_files=True,
            key="no_prefix"
        )
        
    with col2:
        st.subheader("With prefix")
        st.caption("Prefix = first 5 chars of filename + '_'")
        files_yes = st.file_uploader(
            "Upload files (with prefix)",
            type=file_types,
            accept_multiple_files=True,
            key="with_prefix"
        )
        
    return files_no or [], files_yes or []

def display_dataframe_viewer(combined_groups: dict):
    st.subheader("View combined data")
    group_list = sorted(combined_groups.keys())
    selected = st.selectbox("Select group:", group_list)

    if selected:
        df = combined_groups[selected]
        st.subheader(f"{selected} – {len(df):,} rows × {len(df.columns)} columns")

        if len(df) > 50000:
            st.warning("Large table (>50k rows) — showing first 1,000 rows only.")

        st.dataframe(df.head(1000), use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download combined group as CSV",
            csv,
            f"combined_{selected}.csv",
            "text/csv"
        )
