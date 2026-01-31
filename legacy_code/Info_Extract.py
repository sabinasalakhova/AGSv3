### Step 0 Import and Initialize---------------------------------------
import PySimpleGUI as sg
import os.path
import numpy as np
import pandas as pd
from Search_KeyWord import Search_KeyWord
from Match_Soil import Match_Soil
from Search_Depth import Search_Depth

def Info_Extract():
    """
    Promptes the user to open either of the two subfunctions.
    
    Called by: 
    -AGS_Processor_Main
    
    Dependent functions:
    - Search_KeyWord (a function that looks for keywords at all depths in the combined AGS file)
    - Match_Soil (a function that matches soil types and grain sizes)
    - Search_Depth (a function that extracts data at certain depths or depth ranges)
          
    """
    ### Step 1: Initializing for further processing
    # Adding a touch of color
    sg.theme('DarkGreen') 
    default_font = 'Calibri 10'
    table_font = 'Calibri 8'
    
    ### Step 2: Defining the "main" layout of the popup window
    info_extract_layout = [
        [
            # Row 0
            sg.Text("Please select information you would like to extract:", font = default_font),
        ],
        [
            # Row 1
            sg.Button("Seaching a keyword from combined AGS data",pad=(5,5),font = default_font, size = (48,1)),
        ],
        [
            # Row 2
            sg.Button("Matching soil type and grain size",pad=(5,5),font = default_font, size = (48,1)),
        ],
        [
            # Row 3
            sg.Button("Query data at specific depths",pad=(5,5),font = default_font, size = (48,1)),
        ],
    ]
    
    ### Step 3 - Creating Window----------------------------------------------------
    info_extract_window = sg.Window("Information Extraction", layout = info_extract_layout, resizable = True, element_justification = "top")
    
    ### Step 4 - Event Loop: Where magic happens (or not)---------------------------
    while True:
        event, values = info_extract_window.read()
        
        if event == None or event == 'OK': # if user closes window or clicks cancel
            break
            
        elif event == "Seaching a keyword from combined AGS data":
            Search_KeyWord()
            
        elif event == "Matching soil type and grain size":
            Match_Soil()
        
        elif event == "Query data at specific depths":
            Search_Depth()
        
    ### Step 5 - Close your window when break out of while loop!--------------------        
    info_extract_window.close()
        