### Step 0 Import and Initialize---------------------------------------
import PySimpleGUI as sg
import os.path
import numpy as np
import pandas as pd

def Search_KeyWord():
    """
    Looks for keywords in 'GEOL_DESC' and 'Details' columns at all depths in the Combined AGS file
    
    Called by: 
    - Info_Extract
    
    Dependent functions:
    - (none)
    
    Supports reading ONE file only.
    
    Inputs:
    *** The files input here is STRONGLY ADVISED to be the output from Combine AGS function (Combine_AGS.py) such that all exceptions are well handled.
    
    User inputs prompted:
    - Combined AGS file to process
    - Keyword(s) to look for
       
    Outputs:
    Combined AGS file with additional columns stating whether the keyword(s) are present (TRUE/FALSE).
    """
    
    ### Step 1: Initializing for further processing
    # Adding a touch of color
    sg.theme('DarkGreen') 
    default_font = 'Calibri 10'
    table_font = 'Calibri 8'
    kw_list = []
    NR_text = 'no recovery'
    
    ### Step 2: Defining the "main" layout of the popup window
    search_keyword_layout = [
                [
                    # Row 0
                    sg.Text("Please list the keyword(s) you would like to search from GEOL and DETL columns below:", font = default_font),
                ],
                [
                    # Row 1
                    sg.Text("Add keyword:", font = default_font),
                    sg.Input(size=(20,1), font = default_font, key = "-ADD-IN-TEXT-", expand_x = True),
                    sg.Button("Add to List",pad=(5,5),font = default_font, size = (12,1)),
                ],
                [  # Row 2 (Listbox for selected keywords)
                    sg.Listbox(
                        values = kw_list,
                        select_mode = "LISTBOX_SELECT_MODE_SINGLE",
                        enable_events = True,
                        size = (30,9),
                        key = "-KEYWORD LIST-",
                        no_scrollbar = False,
                        expand_x = True,
                        expand_y = True,
                    ),
                ],
                [
                    # Row 3
                    sg.Button("Remove Selected",pad=(5,5),font = default_font, size = (18,1)),
                    sg.Button("Remove All",pad=(5,5),font = default_font, size = (18,1)),
                    sg.Push(),
                ],
                [
                    # Row 4
                    sg.FileBrowse(button_text = "Search from File: ", target = '-SEARCHKW-INPUT-FDIR-', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5), font = default_font, size = (18,1)),
                    sg.Input(size=(50,1), font = default_font, key = '-SEARCHKW-INPUT-FDIR-'),
                ],
                [
                    # Row 5
                    sg.FileSaveAs(button_text = "Save as Excel File: ", target = '-SEARCHKW-OUT-FDIR-', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5), font = default_font, size = (18,1)),
                    sg.Input(size=(50,1), font = default_font, key = '-SEARCHKW-OUT-FDIR-'),        
                ],
                [
                    # Row 6
                    sg.Push(),
                    sg.Button("Search",pad=(5,5),font = default_font, size = (12,1)),
                ],
            ]

    ### Step 3 - Creating Window----------------------------------------------------
    search_keyword_window = sg.Window("Search Keyword", layout = search_keyword_layout, resizable = True, element_justification = "top")
    
    ### Step 4 - Event Loop: Where magic happens (or not)---------------------------
    while True:
        event, values = search_keyword_window.read()
        
        if event == None or event == 'OK': # if user closes window or clicks cancel
            break
        
        elif event == "Add to List": # When user wants to add a keyword to the list
            if len(values['-ADD-IN-TEXT-']) != 0: # Add only when the input bar is not empty
                kw_list.append(values['-ADD-IN-TEXT-'])
                search_keyword_window['-ADD-IN-TEXT-'].update('')
                search_keyword_window['-KEYWORD LIST-'].update(kw_list)
            
        elif event == "Remove Selected":
            if len(values['-KEYWORD LIST-']) != 0:
                if len(values['-KEYWORD LIST-'][0]) != 0: # Removes only if a keyword is selected
                    kw_list.remove(values['-KEYWORD LIST-'][0])
                    search_keyword_window['-KEYWORD LIST-'].update(kw_list)
        
        elif event == "Remove All":
            kw_list.clear()
            search_keyword_window['-KEYWORD LIST-'].update(kw_list)

        elif event == "Search":
            ## Check No.1: Checks if the user has selected a file
            if len(values['-SEARCHKW-INPUT-FDIR-']) == 0:
                sg.popup("Please select one input file to process!", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
            ## Check No.2: Checks if the user has specified output directory
            elif len(values['-SEARCHKW-OUT-FDIR-']) == 0:
                sg.popup("Please specify output directory!", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
            else:
                df_in = pd.read_excel(values['-SEARCHKW-INPUT-FDIR-'])
                if ('GEOL_DESC' not in df_in.columns) | ('Details' not in df_in.columns):
                    sg.popup("Geological descriptions ('GEOL_DESC') column and/or \n Details ('Details') column is not found in the input excel. \n Please make sure that: \n (1) the first row of the excel is the headers and \n (2) 'GEOL_DESC' and 'Details' columns are in the input excel.", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 30,)
                else:
                    for k in range(len(kw_list)):
                        if kw_list[k].casefold() == NR_text.casefold():
                            if ('FI' not in df_in.columns):
                                sg.popup("Warning: 'FI' column is not found in the input excel. Search result will only be based on 'GEOL_DESC' and 'Details' columns.")
                                df_in['No Recovery'] = (df_in['GEOL_DESC'].str.contains(kw_list[k], case = False))|(df_in['Details'].str.contains(kw_list[k], case = False))
                            else:
                                df_in['No Recovery'] = (df_in['GEOL_DESC'].str.contains(kw_list[k], case = False))|(df_in['Details'].str.contains(kw_list[k], case = False))|((df_in['FI'].str.contains('N'))&(df_in['FI'].str.contains('R')))
                        else:
                            df_in[str(kw_list[k])] = (df_in['GEOL_DESC'].str.contains(kw_list[k], case = False))|(df_in['Details'].str.contains(kw_list[k], case = False))
                    df_in.to_excel(values['-SEARCHKW-OUT-FDIR-'])
                        
    ### Step 5 - Close your window when break out of while loop!--------------------        
    search_keyword_window.close()