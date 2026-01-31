### Step 1 Import and Initialize---------------------------------------
import PySimpleGUI as sg
import os.path
import numpy as np
import pandas as pd
from View_single_AGS import View_single_AGS
from Concat_AGS import Concat_AGS

def AGS_Excel():
    ### Aim of AGS_Excel---------------------------------------------------------
    """
    Parses and concatenates AGS3 files.
    
    Called by:
    AGS_Processor_Main
    
    Dependent functions:
    -View_single_AGS
    -Concat_AGS
    
    Ideas based on existing module which handles AGS4:
    https://gitlab.com/ags-data-format-wg/ags-python-library/-/tree/main

    With modifications to local exceptions and practice in Hong Kong.
    -------------
    Inputs:
    - 1 or more than 1 AGS (*.ags) file(s) in AGS3 format.

    Outputs:
    - Excel with data in different groups stored as different tabs.
    - Preserves data in ALL groups! ALL groups! ALL groups!

    Exceptions handled:
    <UNITS> row
    <CONT> row

    """

    # Adding a touch of color
    sg.theme('DarkGreen') 
    default_font = 'Calibri 10'
    table_font = 'Calibri 8'

    ### Step 2 - Defining subfunctions which will be called later
    #(None here, moved to Concat_AGS)
    ### Step 3 - Other initializing processes???
    file_path_accu = []  # Creating an empty list for adding and storing selected file paths
    ### Step 4 - Defining Window Layouts--------------------------------------------
    ## Main Layout
    excel_layout = [
        [
            # Row 1
            sg.Button("Add Files to Selection",pad=(5,5),font = default_font, size = (24,1)),
        ],
        [
            # Row 2
            sg.Text("Selected AGS Files:",font = default_font),
            sg.Push(),
            sg.Button("Clear Selection",pad=(5,5),font = default_font, size = (18,1)),
            sg.Button("Inspect Single AGS",pad=(5,5),font = default_font, size = (18,1)),
        ],
        [
            # Row 3
            sg.Listbox(
                values=[],
                select_mode = "LISTBOX_SELECT_MODE_SINGLE",
                enable_events=True,
                key="-FILE LIST-",
                no_scrollbar = False,
                expand_x = True,
                expand_y = True,
            ),
        ],
        [
            # Adding space
            sg.VPush(),
        ],
        [
            # Last Row
            sg.Push(), # Pushes to the right
            sg.Button("Concatenate",pad=(5,5),font = default_font, size = (12,1)),
        ]
    ]

    ### Step 5 - Creating Window----------------------------------------------------
    window = sg.Window("Select AGS Files to Process", excel_layout, size = (800,400), resizable = True, element_justification = "top")

    ### Step 6 - Event Loop: Where magic happens (or not)---------------------------
    while True:
        event, values = window.read()
        if event == None or event == 'Exit': # if user closes window or clicks cancel
            break
        elif event == 'Add Files to Selection': # prompt the user to select AGS files
            file_paths = sg.popup_get_file(message = "Select AGS Files to Import...",no_window = True, file_types = (('AGS Files', '*.ags'),), multiple_files = True)
            file_path_accu = file_path_accu + list(file_paths)
            fnames_short = []
            for f in file_path_accu:
                fnames_short.append(os.path.basename(f)) # Getting a list of shortened file names (instead of full path) for display
            fnames_short = tuple(fnames_short)
            window["-FILE LIST-"].update(fnames_short) # Displays only the shortened filenames
        elif event == 'Clear Selection': # Clears the list on display if the user wishes to re-select
            file_path_accu = []
            fnames_short = []
            file_paths = []
            window["-FILE LIST-"].update(fnames_short)
        elif event == 'Inspect Single AGS':
            for fdir in file_path_accu:
                if os.path.basename(fdir) == values['-FILE LIST-'][0]:
                    f_dir = os.path.dirname(fdir)
                    break
            try:
                View_single_AGS(os.path.join(f_dir,values['-FILE LIST-'][0]))
            except IndexError:
                sg.popup("Please select at least one AGS file!")
            except UnboundLocalError:
                sg.popup("Please select at least one AGS file!")
            except TypeError:
                print(f_dir, values['-FILE LIST-'])
        elif event == 'Concatenate':
            file_type_checksum = 0 # Checks if any selected file is not ags file
            for f in range(len(file_path_accu)):
                if (file_path_accu[f].endswith("ags"))|(file_path_accu[f].endswith("AGS")):
                    file_type_checksum += 1
                else:
                    file_type_checksum = file_type_checksum
            if len(fnames_short) >= 1 and len(fnames_short) == file_type_checksum:
                Concat_AGS(file_path_accu)
            elif len(fnames_short) != file_type_checksum:
                sg.popup("At least one file selected is not AGS file. Please double check.", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
            else:
                sg.popup("Please select at least one AGS file!", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
    
    ### Step 7 - Close your window when break out of while loop!--------------------        
    window.close()