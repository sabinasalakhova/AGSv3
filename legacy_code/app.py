### Main Function of AGS Processor ###
"""
This is the script that calls out the main window of the AGS Processor. All Subfunctions shall be called within the event loop in this script.

Credits:
Original Ideas: Philip Wu @Aurecon
AGS_Concat: Regine Tsui @Aurecon
AGS_Combine: Christopher Ng @Aurecon
UglyInterface Design: Christopher Ng @Aurecon
"""

### 1 - Importing----------------------------------------------
import PySimpleGUI as sg
import os.path
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd
from AGS_Excel import AGS_Excel
from Combine_AGS import Combine_AGS
from Info_Extract import Info_Extract

# Adding a touch of color
sg.theme('DarkGreen') 
default_font = 'Calibri 10'
table_font = 'Calibri 8'

### 2 - Defining Window Layout-----------------------------------
layout = [
    [
        sg.Button('AGS to Excel',pad=(5,5),font = default_font, size = (12,2)), 
        sg.Text("Step 1. Turns and concatenates one (or more) AGS files to .xlsx file.",pad=(5,5),font = default_font,),        
    ],
    [
        sg.Button('Combine Data',pad=(5,5),font = default_font, size = (12,2)),
        sg.Text("Step 2. Combines data in different groups in one (or more) xlsx files into single-tabbed .xlsx file.",pad=(5,5),font = default_font,), 
    ],
    [
        sg.Button('Information Extraction',pad=(5,5),font = default_font, size = (12,2)),
        sg.Text("Step 3. Extract desired information from combined .xlsx file.",pad=(5,5),font = default_font,),                
    ],
    [
        sg.Button('Calculate Rockhead',pad=(5,5),font = default_font, size = (12,2)),
        sg.Button('Corestone Percentage',pad=(5,5),font = default_font, size = (12,2)),
        sg.Text("Descriptive text (to be updated)",pad=(5,5),font = default_font,),
    ],
    [
        sg.Button('Define Weak Seam',pad=(5,5),font = default_font, size = (12,2)),
        sg.Text("Descriptive text (to be updated)",pad=(5,5),font = default_font,),
    ],
    [
        sg.Button('Calculate Q-value',pad=(5,5),font = default_font, size = (12,2)),
        sg.Text("Descriptive text (to be updated)",pad=(5,5),font = default_font,),
    ],
    [
        sg.VPush(),
    ],
    [
#        sg.Text(data_too_long,text_color = 'Red'),
        sg.Push(),
#        sg.Button('Export Data',pad=(5,5),font = default_font, size = (12,1)),
        sg.Button('Exit',pad=(5,5),font = default_font, size = (12,1))
    ]
]
 
### 3 - Creating Window--------------------------------------------
window = sg.Window("AGS Processor v1", layout, size = (1000,450), resizable = True, element_justification = "top")
  
### 4 - Event Loop: Where magic happens (or not)-------------------
while True:
    event, values = window.read()
    if event == None or event == 'Exit': # if user closes window or clicks cancel
        break
    elif event == 'AGS to Excel':
        AGS_Excel()
        #sg.popup('This function is under development!',title = 'Sorry!', font = default_font)
    elif event == 'Combine Data':
        Combine_AGS()
    elif event == 'Information Extraction':
        Info_Extract()
    elif event == 'Calculate Rockhead':
        sg.popup('This function is under development!',title = 'Sorry!', font = default_font)
    elif event == 'Define Weak Seam':
        sg.popup('This function is under development!',title = 'Sorry!', font = default_font)
    elif event == 'Corestone Percentage':
        sg.popup('This function is under development!',title = 'Sorry!', font = default_font)
    elif event == 'Calculate Q-value':
        sg.popup('This function is under development!',title = 'Sorry!', font = default_font)
    
### 5 - Close your window when break out of while loop!------------        
window.close()