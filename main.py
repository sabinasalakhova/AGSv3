import streamlit as st
import re
from src.ui.components import setup_page, display_file_uploaders, display_dataframe_viewer
from src.parsing import get_parser
from src.parsing.utils import detect_ags_version
from src.processing.combiner import combine_files, expand_rows
from src.domain.models import AGSVersion, ParsedAGSFile

def main():
    setup_page()
    
    # 1. Configuration
    st.subheader("Select AGS version mode")
    mode = st.radio(
        "Choose version (prevents mixing AGS3 and AGS4)",
        options=["AGS3 (legacy)", "AGS4 (modern)"],
        horizontal=True,
        index=1
    )
    target_version_str = "AGS3" if "AGS3" in mode else "AGS4"
    
    # 2. Upload
    files_no_prefix, files_with_prefix = display_file_uploaders()
    all_files = []
    
    # helper to organize (file, needs_prefix)
    if files_no_prefix:
        all_files.extend([(f, False) for f in files_no_prefix])
    if files_with_prefix:
        all_files.extend([(f, True) for f in files_with_prefix])

    if not all_files:
        st.info("Upload at least one file in one or both sections.")
        return

    st.success(f"**{len(all_files)} file(s)** ready for processing in **{target_version_str}** mode")
    
    # 3. Processing
    parsed_results = []
    failed_files = []
    
    with st.status("Processing files…", expanded=True) as status:
        for idx, (file_obj, needs_prefix) in enumerate(all_files, 1):
            fname = file_obj.name
            status.update(label=f"Processing {fname} ({idx}/{len(all_files)})")
            
            try:
                content = file_obj.getvalue()
                
                # A. Detect Version
                detected = detect_ags_version(content)
                if target_version_str == "AGS3" and detected == "AGS4":
                     raise ValueError("Detected AGS4 file in AGS3 mode.")
                if target_version_str == "AGS4" and detected == "AGS3":
                     raise ValueError("Detected AGS3 file in AGS4 mode.")
                     
                # B. Parse
                parser = get_parser(target_version_str)
                parsed_file = parser.parse(content, fname)
                
                if not parsed_file.is_valid:
                    error_msg = "; ".join([e.message for e in parsed_file.errors])
                    raise ValueError(f"Parsing failed: {error_msg}")
                    
                if not parsed_file.groups:
                    raise ValueError("No valid groups found.")
                
                # C. Apply Prefix (in-memory modifier on the dataframe)
                if needs_prefix:
                    base = fname.split('.')[0].upper()
                    # Sanitize prefix (alphanumeric only, max 5 chars)
                    prefix = re.sub(r'[^A-Z0-9]', '', base)[:5] + "_"
                    st.write(f"Applying prefix '{prefix}' for {fname}")
                    
                    for group, df in parsed_file.groups.items():
                        # Simple heuristic: find 'HOLE_ID' or 'LOCA_ID'
                        cols = df.columns
                        target_col = next((c for c in cols if c in ['HOLE_ID', 'LOCA_ID', 'HOLEID']), None)
                        if target_col:
                            df[target_col] = prefix + df[target_col].astype(str).str.strip()

                parsed_results.append(parsed_file)
                st.write(f"✅ Success: {fname}")
                
            except Exception as e:
                failed_files.append({"File": fname, "Error": str(e)})
                st.error(f"❌ Failed {fname}: {e}")

    # 4. Results & Combining
    if failed_files:
        st.error(f"{len(failed_files)} files failed.")
        st.dataframe(failed_files)
        
    if not parsed_results:
        st.warning("No files successfully parsed.")
        return
        
    st.write("Combining groups...")
    combined_groups = combine_files(parsed_results)
    
    # 5. Viewing
    display_dataframe_viewer(combined_groups)

if __name__ == "__main__":
    main()
