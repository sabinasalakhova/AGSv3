### Step 0 Import and Initialize---------------------------------------
import PySimpleGUI as sg
import os.path
import numpy as np
import pandas as pd

def Search_Depth():
    """
    Extracts data at certain depths or depth ranges.
    
    Called by: 
    - Info_Extract
    
    Dependent functions:
    - (none)
    
    Supports reading ONE file only.
    
    Inputs:
    *** Original dataframe
    *** List of depths: Any excel file with the following format:
    GIU_HOLE_ID (e.g. 62392_ARQ04-BH-01) | DEPTH_FROM (e.g. 15) (in meters) | DEPTH_TO (e.g. 20) (in meters)
    
    User inputs prompted:
       
    Outputs:

    """
    ### Step 1: Initializing for further processing
    # Adding a touch of color
    sg.theme('DarkGreen') 
    default_font = 'Calibri 10'
    table_font = 'Calibri 8'
    
    column_checklist_single = ['GIU_HOLE_ID', 'DEPTH']
    column_checklist_range = ['GIU_HOLE_ID', 'DEPTH_FROM', 'DEPTH_TO']
    col_not_append = ['Unnamed: 0','GIU_NO','HOLE_ID']
    
    ### Step 2: Defining the "main" layout of the popup window
    search_depth_layout = [
                [
                    # Row 0
                    sg.FileBrowse(button_text = "Combined Data Excel: ", target = '-SEARCHDEPTH-DATA-FDIR-', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5), font = default_font, size = (24,1)),
                    sg.Input(size=(50,1), font = default_font, key = '-SEARCHDEPTH-DATA-FDIR-'),
                ],
                [
                    # Row 1
                    sg.FileBrowse(button_text = "Depth Excel to Search: ", target = '-SEARCHDEPTH-INPUT-FDIR-', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5), font = default_font, size = (24,1)),
                    sg.Input(size=(50,1), font = default_font, key = '-SEARCHDEPTH-INPUT-FDIR-'),
                ],
                [
                    # Row 2
                    sg.Text('The Depth data is in the format of: ', font = default_font),
                    sg.Radio('Single Depth Points', group_id = 1, font = default_font, key = '-TICK-SINGLE-'),
                    sg.Radio('From & To Depth Ranges', group_id = 1, font = default_font, key = '-TICK-RANGE-'),
                ],
                [
                    # Row 3
                    sg.FileSaveAs(button_text = "Save as Excel File: ", target = '-SEARCHDEPTH-OUT-FDIR-', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5), font = default_font, size = (24,1)),
                    sg.Input(size=(50,1), font = default_font, key = '-SEARCHDEPTH-OUT-FDIR-'),        
                ],
                [
                    # Row 4
                    sg.Push(),
                    sg.Button("Search",pad=(5,5), font = default_font, size = (12,1)),
                ],
            ]
      
    ### Step 3 - Creating Window----------------------------------------------------
    search_depth_window = sg.Window("Match Soil Types and Grain Sizes", layout = search_depth_layout, resizable = True, element_justification = "top")
    
    ### Step 4 - Event Loop: Where magic happens (or not)---------------------------
    while True:
        event, values = search_depth_window.read()
        
        if event == None or event == 'OK': # if user closes window or clicks cancel
            break
        
        elif event == 'Search':
            data_xls = pd.ExcelFile(values['-SEARCHDEPTH-DATA-FDIR-'])
            input_xls = pd.ExcelFile(values['-SEARCHDEPTH-INPUT-FDIR-'])
            if len(data_xls.sheet_names)>1 | len(input_xls.sheet_names)>1:
                sg.popup('Multiple sheets detected in either Combined Data Excel and/or Depth Excel to Search. Only the data in the first sheet will be read.', title = "Warning")
            df_data = pd.read_excel(values['-SEARCHDEPTH-DATA-FDIR-']) # from Combined Data Excel
            df_in = pd.read_excel(values['-SEARCHDEPTH-INPUT-FDIR-']) # from Depth Excel
            if (((values['-TICK-SINGLE-'] == True)&(len(df_data.columns)>=2)&(len(df_in.columns)>=2)) | ((values['-TICK-RANGE-'] == True)&(len(df_data.columns)>=3)&(len(df_in.columns)>=3))): ## Check No.1: Whether the combined data excel and depth excel has enough headings
                if ((values['-TICK-SINGLE-'] == True)&(all (cols in df_data.columns for cols in column_checklist_range))&(all (cols2 in df_in.columns for cols2 in column_checklist_single))) | ((values['-TICK-RANGE-'] == True)&(all (cols3 in df_data.columns for cols3 in column_checklist_range))&(all (cols4 in df_in.columns for cols4 in column_checklist_range))): # Check No.2: Whether the required columns are in the combined data excel and input excel
                    new_col = df_in.columns.tolist()
                    add_col = []
                    for col5 in df_data.columns.tolist():
                        if (col5 not in new_col)&(col5 not in col_not_append):
                            new_col.append(col5)
                            add_col.append(col5)
                    df=pd.DataFrame(columns = new_col)
                    if values['-TICK-SINGLE-'] == True: ## Case 1: Single Depth Query----------------------------------------------------------------------------------------------
                        row_index = 0
#                         for s in range(len(df_in)):
#                             df_hole = df_data.loc[(df_data.GIU_HOLE_ID==df_in.loc[s,'GIU_HOLE_ID'])]
#                             if df_in.loc[s,'DEPTH'] not in list(df_hole['DEPTH_FROM'])+list(df_hole['DEPTH_TO'].tail(1)): # if the queried depth is not one of the existing depth intervals
#                                 for col6 in df_in.columns.tolist():
#                                     df.loc[row_index,col6] = df_in.loc[s,col6]
#                                 for col7 in add_col:
#                                     df.loc[row_index,col7] = df_data.loc[(df_data.GIU_HOLE_ID==df_in.loc[s,'GIU_HOLE_ID'])&df_data.DEPTH_FROM.between(,, inclusive = 'left')]
#                     if values['-TICK-RANGE-'] == True:  ## Case 2: Depth Range Query----------------------------------------------------------------------------------------------
#                         all_depths = []
                        
                        df.to_excel(values['-SEARCHDEPTH-OUT-FDIR-'])
                else: ## Exit for Check No.2
                    if values['-TICK-SINGLE-'] == True:
                        sg.popup('At least one of the following column headings are missing: '+str(column_checklist_single), font = default_font, title = "Sorry!", auto_close = True, auto_close_duration = 15)
                    if values['-TICK-RANGE-'] == True:
                        sg.popup('At least one of the following column headings are missing: '+str(column_checklist_range), font = default_font, title = "Sorry!", auto_close = True, auto_close_duration = 15)
            else: ## Exit for Check No.1 
                sg.popup('The number of column headings in Depth Excel and/or Combined Data Excel is insufficient. Please make sure that the first row of the excel(s) are the column headings.', font = default_font, title = "Sorry!", auto_close = True, auto_close_duration = 15)
                
    search_depth_window.close()
            
            