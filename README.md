# AGS File Processor (AGSv3)

An interactive web application for processing, validation, and combining AGS (Association of Geotechnical and Geoenvironmental Specialists) files.

## Features

- **Multi-Version Support**: Handles both AGS3 (Legacy) and AGS4 (Modern) files.
- **Robust Parsing**: 
  - Uses the official `python-ags4` library for strict AGS4 compliance.
  - Includes a custom parser for legacy AGS3 support.
- **Data Combination**: Merges groups from multiple files into single datasets.
- **Performance**: Optimized processing for large geotechnical datasets.
- **Privacy First**: All processing happens locally in your browser session.

## Architecture

This project follows a **Clean Architecture** approach:

```text
AGSv3/
├── main.py              # Application Entry Point (UI Orchestrator)
├── pyproject.toml       # Dependency Management (Poetry)
├── src/                 # Source Code
│   ├── domain/          # Shared Models (data classes, enums)
│   ├── parsing/         # Parser Strategies (AGS3/AGS4)
│   ├── processing/      # Business Logic (Combining, Cleaning)
│   └── ui/              # Reusable UI Components
└── legacy_code/         # Archived "Version 1" desktop app (PySimpleGUI)
```

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

1.  **Install Poetry** (if you haven't already).
2.  **Install Dependencies**:
    ```bash
    poetry install
    ```

Alternatively, you can install via pip:
```bash
pip install streamlit pandas python-ags4 openpyxl
```

## Usage

To run the web application:

```bash
streamlit run main.py
```

## Legacy Code
The `legacy_code/` directory contains an older desktop-based version of the tool (AGS Processor v1) and specialized calculation scripts. These are kept for reference but are not part of the modern web application.

## Support
For issues or questions, please open an issue on the GitHub repository.
