import streamlit as st
import pandas as pd
from typing import List, Tuple, Any
import io
from src.processing.combiner import get_key_data_intervals,get_key_data_intervals_mapped,get_key_data_intervals_full,build_key_data_excel_options

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
            "Download only this group (combines data from all uploaded files) as one sheet in Excel",
            csv,
            f"combined_{selected}.csv",
            "text/csv"
        )

def display_workbook_download(combined_groups: dict):
    st.subheader(" One excel workbook, with all groups at individual sheets")

    if combined_groups:
        # Create Excel workbook with all groups as sheets
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with io.BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                total_groups = len(combined_groups)
                for i, (group, df) in enumerate(sorted(combined_groups.items())):
                    status_text.text(f'Processing sheet: {group}')
                    df.to_excel(writer, sheet_name=group, index=False)
                    progress_bar.progress((i + 1) / total_groups)
            
            status_text.text('Finalizing workbook...')
            buffer.seek(0)
            excel_data = buffer.getvalue()
        
        progress_bar.progress(1.0)
        status_text.text('Workbook ready for download!')

        st.download_button(
            "Download full combined workbook as Excel",
            excel_data,
            "combined_workbook.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Clear progress indicators after successful creation
        progress_bar.empty()
        status_text.empty()

    # Custom group selection for separate workbook
    st.subheader("📋 Custom group selection")
    selected_groups = st.multiselect("Pick groups to combine in one workbook:", sorted(combined_groups.keys()))
    if selected_groups:
        custom_dict = {g: combined_groups[g] for g in selected_groups}
        with io.BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                for group, df in custom_dict.items():
                    df.to_excel(writer, sheet_name=group, index=False)
            buffer.seek(0)
            custom_excel = buffer.getvalue()
        st.download_button("Download selected groups workbook", custom_excel, "custom_groups.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
def display_key_data_workbook(key_data_groups: dict):
    """Ultra-simplified key data display with one-click Excel downloads."""
    
    st.subheader("Key Data Combined by Depth Intervals")

    if not key_data_groups:
        st.warning("No key data groups found (CORE, WETH, GEOL, FRAC, DETL, SAMP)")
        return

    # Custom group selection before mapping
    st.subheader("📋 Select groups for interval mapping")
    available_groups = sorted(key_data_groups.keys())
    selected_key_groups = st.multiselect(
        "Choose which groups to include in depth intervals:",
        available_groups,
        default=available_groups,  # All selected by default
        key="key_data_groups"
    )
    
    if not selected_key_groups:
        st.warning("Please select at least one group to proceed.")
        return
    
    # Filter the key data groups based on selection
    filtered_key_data = {k: v for k, v in key_data_groups.items() if k in selected_key_groups}

    # Add button to trigger processing
    if st.button("🔄 Generate Key Data Intervals", type="primary"):
        # Build all Excel options at once
        progress = st.progress(0)
        status = st.empty()
        
        status.text("Building Excel files...")
        progress.progress(0.5)
        
        excel_options = build_key_data_excel_options(filtered_key_data)
        
        progress.progress(1.0)
        status.text("Ready!")
        
        if not excel_options:
            st.error("No data could be processed into intervals.")
            progress.empty()
            status.empty()
            return

        # Quick preview + download buttons (removed raw groups)
        st.subheader("📊 Preview & Download")
        
        cols = st.columns(len(excel_options))
        
        for i, (option_name, excel_bytes) in enumerate(excel_options.items()):
            with cols[i % len(cols)]:
                st.write(f"**{option_name}**")
                
                # Show quick preview (only mapped and full intervals)
                if option_name == "Mapped Intervals":
                    df = get_key_data_intervals_mapped(filtered_key_data)
                elif option_name == "Full Intervals":
                    df = get_key_data_intervals_full(filtered_key_data)
                else:
                    continue  # Skip raw groups
                
                if not df.empty:
                    st.caption(f"{len(df):,} rows × {len(df.columns)} columns")
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    # One-click download
                    filename = f"key_data_{option_name.lower().replace(' ', '_')}.xlsx"
                    st.download_button(
                        f"📥 Download {option_name}",
                        excel_bytes,
                        filename,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{i}",
                        use_container_width=True
                    )

        # Clear progress
        progress.empty()
        status.empty()
    else:
        st.info(f"Selected {len(selected_key_groups)} groups. Click the button above to generate depth intervals.")