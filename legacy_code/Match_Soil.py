### Step 0 Import and Initialize---------------------------------------
import PySimpleGUI as sg
import os.path
import numpy as np
import pandas as pd

def Match_Soil():
    """
    Matches soil types and grain sizes.
    
    Called by: 
    - Info_Extract
    
    Dependent functions:
    - (none)
    
    Supports reading ONE file only.
    
    Inputs:
    *** Original dataframe
    
    User inputs prompted:
    - Combined AGS file to process
    - Soil Types and grain sizes to match
       
    Outputs:
    Combined AGS file with an additional column stating the soil type matched with grain size (e.g. All-c/z).
    
    Possible ways to extend:
    Read the number of sheets in input excel and set a popup for the user to choose which sheet to process. Skipped due to limited time.
    """
    ### Step 1: Initializing for further processing
    # Adding a touch of color
    sg.theme('DarkGreen') 
    default_font = 'Calibri 10'
    table_font = 'Calibri 8'
    st_list = ['IV', 'V', 'VI (RESIDUAL SOIL)', 'TOPSOIL', 'MARINE DEPOSIT', 'ALLUVIUM', 'COLLUVIUM', 'FILL','ESTUARINE DEPOSIT'] # list of predefined soil types
    gs_list = ['CLAY', 'FINE', 'SILT', 'SAND', 'GRAVEL', 'COBBLE', 'BOULDER'] # list of predefined grain sizes
    
    ### Step 2: Defining the "main" layout of the popup window
    match_soil_layout = [
                [
                    # Row 0---------------Soil types--------------------------------
                    sg.Text("Soil Types to match:", font = default_font),
                ],
                [
                    # Row 1
                    sg.Text("Add soil type:", font = default_font),
                    sg.Input(size=(20,1), font = default_font, key = "-ADD-IN-SOIL-", expand_x = True),
                    sg.Button("Add Soil Type",pad=(5,5),font = default_font, size = (12,1)),
                ],
                [  # Row 2 (Listbox for selected soil types)
                    sg.Listbox(
                        values = st_list,
                        select_mode = "LISTBOX_SELECT_MODE_SINGLE",
                        enable_events = True,
                        size = (30,9),
                        key = '-SOIL-TYPE-LIST-',
                        no_scrollbar = False,
                        expand_x = True,
                        expand_y = True,
                    ),
                ],
                [
                    # Row 3
                    sg.Button("Remove Selected Soil",pad=(5,5),font = default_font, size = (18,1)),
                    sg.Button("Remove All Soils",pad=(5,5),font = default_font, size = (18,1)),
                    sg.Push(),
                ],
                [
                    # Row 4-----------Grain sizes-----------------------------------
                    sg.Text("Grain Sizes to match:", font = default_font),
                ],
                [
                    # Row 5
                    sg.Text("Add grain size:", font = default_font),
                    sg.Input(size=(20,1), font = default_font, key = "-ADD-IN-SIZE-", expand_x = True),
                    sg.Button("Add Grain Size",pad=(5,5),font = default_font, size = (12,1)),
                ],
                [  # Row 6 (Listbox for selected grain sizes)
                    sg.Listbox(
                        values = gs_list,
                        select_mode = "LISTBOX_SELECT_MODE_SINGLE",
                        enable_events = True,
                        size = (30,9),
                        key = '-GRAIN-SIZE-LIST-',
                        no_scrollbar = False,
                        expand_x = True,
                        expand_y = True,
                    ),
                ],
                [
                    # Row 7
                    sg.Button("Remove Selected Size",pad=(5,5),font = default_font, size = (18,1)),
                    sg.Button("Remove All Sizes",pad=(5,5),font = default_font, size = (18,1)),
                    sg.Push(),
                ],
                [
                    # Row 8
                    sg.FileBrowse(button_text = "Search from File: ", target = '-MATCHSOIL-INPUT-FDIR-', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5), font = default_font, size = (18,1)),
                    sg.Input(size=(50,1), font = default_font, key = '-MATCHSOIL-INPUT-FDIR-'),
                ],
                [
                    # Row 9
                    sg.FileSaveAs(button_text = "Save as Excel File: ", target = '-MATCHSOIL-OUT-FDIR-', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5), font = default_font, size = (18,1)),
                    sg.Input(size=(50,1), font = default_font, key = '-MATCHSOIL-OUT-FDIR-'),        
                ],
                [
                    # Row 10
                    sg.Push(),
                    sg.Button("Match",pad=(5,5),font = default_font, size = (12,1)),
                ],
            ]

    ### Step 3 - Creating Window----------------------------------------------------
    match_soil_window = sg.Window("Match Soil Types and Grain Sizes", layout = match_soil_layout, resizable = True, element_justification = "top")
    
    ### Step 4 - Event Loop: Where magic happens (or not)---------------------------
    while True:
        event, values = match_soil_window.read()
        
        if event == None or event == 'OK': # if user closes window or clicks cancel
            break
        
        elif event == "Add Soil Type": #--------------Soil types-------------------
            if len(values['-ADD-IN-SOIL-']) != 0: # Add only when the input bar is not empty
                st_list.append(values['-ADD-IN-SOIL-'])
                match_soil_window['-ADD-IN-SOIL-'].update('')
                match_soil_window['-SOIL-TYPE-LIST-'].update(st_list)
            
        elif event == "Remove Selected Soil":
            if len(values['-SOIL-TYPE-LIST-']) != 0:
                if len(values['-SOIL-TYPE-LIST-'][0]) != 0: # Removes only if a keyword is selected
                    st_list.remove(values['-SOIL-TYPE-LIST-'][0])
                    match_soil_window['-SOIL-TYPE-LIST-'].update(st_list)
        
        elif event == "Remove All Soils":
            st_list.clear()
            match_soil_window['-SOIL-TYPE-LIST-'].update(st_list)
        
        elif event == "Add Grain Size": #--------------grain sizes-------------------
            if len(values['-ADD-IN-SOIL-']) != 0: # Add only when the input bar is not empty
                gs_list.append(values['-ADD-IN-SIZE-'])
                match_soil_window['-ADD-IN-SIZE-'].update('')
                match_soil_window['-GRAIN-SIZE-LIST-'].update(gs_list)
            
        elif event == "Remove Selected Size":
            if len(values['-GRAIN-SIZE-LIST-']) != 0:
                if len(values['-GRAIN-SIZE-LIST-'][0]) != 0: # Removes only if a keyword is selected
                    gs_list.remove(values['-GRAIN-SIZE-LIST-'][0])
                    match_soil_window['-GRAIN-SIZE-LIST-'].update(gs_list)
        
        elif event == "Remove All Sizes":
            gs_list.clear()
            match_soil_window['-GRAIN-SIZE-LIST-'].update(gs_list)
            
        elif event == "Match":
            ## Check No.1: Checks if the user has selected a file
            if len(values['-MATCHSOIL-INPUT-FDIR-']) == 0:
                sg.popup("Please select one input file to process!", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
            ## Check No.2: Checks if the user has specified output directory
            elif len(values['-MATCHSOIL-OUT-FDIR-']) == 0:
                sg.popup("Please specify output directory!", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
            else:
                df_in = pd.read_excel(values['-MATCHSOIL-INPUT-FDIR-'])
                if ('GEOL_DESC' not in df_in.columns) | ('GEOL' not in df_in.columns) | ('Details' not in df_in.columns) | ('WETH' not in df_in.columns):
                    sg.popup("Geological descriptions ('GEOL', 'GEOL_DESC') column and/or \n Details ('Details') column and/or \n Weathing ('WETH') column is/are not found in the input excel. \n Please make sure that: \n (1) the first row of the excel is the headers and \n (2) 'GEOL_DESC' and 'Details' columns are in the input excel.", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 30,)
                else: ### --------------- Actual Code for Matching (** should be adjusted to make sense geologically!) ---------------------------------------------------
                    df = df_in
                    df['Soil Type/Grain Size'] = np.nan
                    df['Grain Size'] = np.nan
                    for s in range(len(st_list)):
                        # Soil Types: find the predefined soil types first
                        if st_list[s] == 'IV' or st_list[s] == 'V':
                            df.loc[(df['WETH'].str.contains(str(st_list[s]), case = True, na = False)),'Soil Type'] = str(st_list[s])
                        elif st_list[s] == 'VI (RESIDUAL SOIL)':
                            df.loc[(df['WETH'].str.contains('VI', case = True, na = False) | df['GEOL_DESC'].str.contains('RESIDUAL SOIL', case = True, na = False)),'Soil Type'] = 'VI'
                        elif st_list[s] == 'TOPSOIL':
                            df.loc[(df['GEOL_DESC'].str.contains('TOPSOIL', case = True, na = False) | df['GEOL'].str.contains('TOPSOIL', case = True, na = False) | df['GEOL_DESC'].str.contains('TOP SOIL', case = True, na = False) | df['GEOL'].str.contains('TOP SOIL', case = True)),'Soil Type'] = 'TS'
                        elif st_list[s] == 'MARINE DEPOSIT':
                            df.loc[(df['GEOL_DESC'].str.contains('MARINE DEPOSIT', case = True, na = False) | df['GEOL'].str.contains('MARINE', case = True, na = False)),'Soil Type'] = 'MD'
                        elif st_list[s] == 'ALLUVIUM':
                            df.loc[(df['GEOL_DESC'].str.contains('ALLUVIUM', case = True, na = False) | df['GEOL'].str.contains('ALL', case = True, na = False)),'Soil Type'] = 'ALL'
                        elif st_list[s] == 'COLLUVIUM':
                            df.loc[(df['GEOL_DESC'].str.contains('COLLUVIUM', case = True, na = False) | df['GEOL'].str.contains('COLL', case = True, na = False)),'Soil Type'] = 'COLL'
                        elif st_list[s] == 'ESTURINE DEPOSIT':
                            df.loc[(df['GEOL_DESC'].str.contains('ESTURINE DEPOSIT', case = True, na = False) | df['GEOL'].str.contains('EST', case = True, na = False)),'Soil Type'] = 'ED'
                        elif st_list[s] == 'FILL':
                            df.loc[(df['GEOL_DESC'].str.contains('FILL', case = True, na = False) | df['GEOL'].str.contains('FILL', case = True, na = False)),'Soil Type'] = 'FILL'
                        else: # for other cases defined by the user. Can't catch anything if the soil type specified is not found. Case sensitive (can change case = False if case insensitive search is needed).
                            df.loc[(df['GEOL_DESC'].str.contains(str(st_list[s]), case = True, na = False) | df['GEOL'].str.contains(str(st_list[s]), case = True, na = False)),'Soil Type'] = str(st_list[s])
                    for g in range(len(gs_list)):
                        # Grain Sizes: find the predefined grain sizes first. Finer soils overwritten by coarser soils
                        if gs_list[g] == 'CLAY':
                            df.loc[(df['GEOL_DESC'].str.contains('CLAY', case = True) | df['GEOL'].str.contains('CLAY', case = True) | df['Details'].str.contains('CLAY',case = True))&(df['Grain Size'].isna()),'Clay'] = 'c'
                        elif gs_list[g] == 'FINE':
                            df.loc[(df['GEOL_DESC'].str.contains('SILT/CLAY', case = True) | df['GEOL'].str.contains('FINE', case = True) | df['Details'].str.contains('FINE',case = True))&(df['Grain Size'].isna()),'Fine'] = 'c/z'
                        elif gs_list[g] == 'SILT':
                            df.loc[(df['GEOL_DESC'].str.contains('SILT', case = True) | df['GEOL'].str.contains('SILT', case = True) | df['Details'].str.contains('SILT',case = True))&(df['Grain Size'].isna()),'Silt'] = 'z'
                            
                        elif gs_list[g] == 'SAND':
                            df.loc[(df['GEOL_DESC'].str.contains('SAND', case = True) | df['GEOL'].str.contains('SAND', case = True) | df['Details'].str.contains('SAND',case = True))&(df['Grain Size'].isna()),'Sand'] = 's'
                            
                        elif gs_list[g] == 'GRAVEL':
                            df.loc[(df['GEOL_DESC'].str.contains('GRAV', case = True) | df['GEOL'].str.contains('GRAV', case = True) | df['Details'].str.contains('GRAV',case = True))&(df['Grain Size'].isna()),'Gravel'] = 'g'
                            
                        elif gs_list[g] == 'COBBLE':
                            df.loc[(df['GEOL_DESC'].str.contains('COBBLE', case = True) | df['GEOL'].str.contains('CBBL', case = True) | df['Details'].str.contains('COBBLE',case = True))&(df['Grain Size'].isna()),'Cobble'] = 'cb'
                            
                        elif gs_list[g] == 'BOULDER':
                            df.loc[(df['GEOL_DESC'].str.contains('BOULDER', case = True) | df['GEOL'].str.contains('BLDR', case = True) | df['Details'].str.contains('BOULDER',case = True))&(df['Grain Size'].isna()),'Boulder'] = 'bd'
                            
                        else:
                            df.loc[(df['GEOL_DESC'].str.contains(str(gs_list[g]), case = True) | df['GEOL'].str.contains(str(gs_list[g]), case = True) | df['Details'].str.contains(str(gs_list[g]),case = False))&(df['Grain Size'].isna()),str(gs_list[g])] = str(gs_list[g])
                    df_gs = df[['Clay','Silt','Sand','Gravel','Cobble','Boulder']]
                    df['Grain Size'] = df_gs.stack().groupby(level=0).apply(lambda x: ','.join(x))
                    df['Soil Type/Grain Size'] = df['Soil Type']+'-'+df['Grain Size']
                    df.pop('Unnamed: 0')
                    df.pop('Soil Type')
                    df.pop('Grain Size')
                    df.to_excel(values['-MATCHSOIL-OUT-FDIR-'])
    ### Step 5 - Close your window when break out of while loop!--------------------        
    match_soil_window.close()