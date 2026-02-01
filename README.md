# AGS File Processor

An interactive web application for processing and combining AGS (Association of Geotechnical and Geoenvironmental Specialists) files.

## Features

- Support for both AGS3 (legacy) and AGS4 (modern) file formats
- Upload and combine multiple AGS files
- Optional prefix addition to HOLE_ID/LOCA_ID columns
- Interactive data viewing and CSV export
- File diagnostics and version validation

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/sabinasalakhova/AGSv3.git
   cd AGSv3
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit pandas python-ags4
   ```

## Running the Application

To run the AGS File Processor web application, use the following command:

```bash
streamlit run workingapp.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

## Usage

1. **Select AGS version mode**: Choose between AGS3 (legacy) or AGS4 (modern) mode
2. **Upload files**: 
   - Upload files without prefix in the left column (keeps original HOLE_ID/LOCA_ID)
   - Upload files with prefix in the right column (adds first 5 alphanumeric characters of filename + '_')
3. **View combined data**: Browse the combined groups and download results as CSV

## File Structure

- `workingapp.py` - Main Streamlit application
- `agsparser.py` - AGS file parsing utilities
- `cleaners.py` - Data cleaning and combining functions
- `ags_data/` - Sample AGS files for testing

## Requirements

- Python 3.7+
- streamlit
- pandas
- python-ags4 (recommended for AGS4 files)

## Support

For issues or questions, please open an issue on the GitHub repository.
