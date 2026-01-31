### Step 0 Import and Initialize---------------------------------------
import PySimpleGUI as sg
import os.path
import numpy as np
import pandas as pd

def Combine_AGS():
    """
    Combines all intervals of AGS Excel files and show the result in a popup window.
    
    Called by: 
    -AGS_Processor_Main
    
    Dependent functions:
    - (none)
    
    Supports reading files in different directories.
    
    Inputs:
    *** The files input here must be the outputs from AGS to Excel function (Concat_AGS.py) such that all exceptions are well handled.
    
    User inputs prompted:
    - file(s) to process
    - GROUPs to combine
       
    Outputs:
    Excel with only one sheet of combined ags files.
    """
    
    ### Step 1: Checking of inputs (if needed) *TODO
    
    ### Step 2: Dependent functions
    def check_second_row(df): ##### Legacy code from development. Not used in the code.
        """
        Checks and removes if the sheet has <UNIT> row.
        """
        if df.HOLE_ID[0] == ('<UNITS>' or '<UNIT>'):
            df = df.drop([0])
        return df

    def clean_geol_cont(GEOL): ##### Legacy code from development. Not used in the code.
        """
        Checks and cleans if the GEOL sheet contains <CONT> rows.
        """
        i=0    #Resets initial index
        for i in range(len(GEOL)): 
            if GEOL.HOLE_ID[i] == '<CONT>':
                GEOL.GEOL_DESC[i-1] = GEOL.GEOL_DESC[i-1]+' '+GEOL.GEOL_DESC[i]
                GEOL.GEOL_LEG[i-1] = GEOL.GEOL_LEG[i]
                GEOL.GEOL_STAT[i-1] = GEOL.GEOL_STAT[i]
                GEOL = GEOL.drop([i])
        return GEOL

    def clean_hole_cont(HOLE): ##### Legacy code from development. Not used in the code.
        """
        Checks and cleans if the HOLE sheet contains <CONT> rows.
        """
        i=0    #Resets initial index
        for i in range(len(GEOL)): ##### Legacy code from development. Not used in the code.
            if GEOL.HOLE_ID[i] == '<CONT>':
                HOLE.HOLE_REM[i-1] = HOLE.HOLE_REM[i-1]+' '+HOLE.HOLE_REM[i]
                HOLE.HOLE_ORNT[i-1] = HOLE.HOLE_ORNT[i]
                HOLE.HOLE_INCL[i-1] = HOLE.HOLE_INCL[i]
                HOLE = HOLE.drop([i])
        return HOLE
    
    ### Step 3: Initializing for further processing
    file_path_accu = [] # Creating an empty list for adding and storing selected file paths
    # Adding a touch of color
    sg.theme('DarkGreen') 
    default_font = 'Calibri 10'
    table_font = 'Calibri 8'
    
    ### Step 4: Defining the "main" layout of the popup window
    combine_layout = [
        [
            # Row 0
            sg.Text("NOTE: Only file(s) from the AGS to Excel function should be selected.", font = default_font),
        ],
        [
            # Row 1
            sg.Button("Add Files to Selection",pad=(5,5),font = default_font, size = (24,1)),
        ],
        [
            # Row 2
            sg.Text("Selected AGS Files:", font = default_font),
            sg.Push(),
            sg.Button("Clear File Selection", pad=(5,5), font = default_font, size = (18,1)),
        ],
        [
            # Row 3
            sg.Listbox(
                values=[],
                select_mode = "LISTBOX_SELECT_MODE_MULTIPLE",
                size = (20, 8),
                enable_events=True,
                key="-EXCEL LIST-",
                no_scrollbar = False,
                expand_x = True,
                expand_y = True,
            ),
        ],
        [
            # Row 4
            sg.Text("Click to highlight and combine data from selected Groups only: \n (all data will be combined if no groups are selected): ", font = default_font),
            sg.Listbox(
                values = ['CORE', 'DETL', 'WETH', 'FRAC', 'GEOL'],
                select_mode = sg.LISTBOX_SELECT_MODE_MULTIPLE,
                enable_events=True,
                size = (12,8),
                key="-GROUP LIST-",
                no_scrollbar = False,
                expand_x = True,
                expand_y = True,
            )
        ],
        [
            # Row 5
            sg.Text("Save as Excel File: ", font = default_font),
            sg.Input(size=(50,1), font = default_font, key = '-COMBINE-OUT-FDIR-'),
            sg.FileSaveAs(button_text = "Browse...", target = '-COMBINE-OUT-FDIR-', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5),font = default_font),
        ],
        [
            # Row 6
            sg.Text("Status: Idle", key = "-STATUS TEXT-", font = default_font),
            sg.Push(),
            sg.Button("Combine", pad=(5,5), font = default_font, size = (18,1),),
        ],
    ]
    
    ### Step 5 - Creating Window----------------------------------------------------
    combine_ags_window = sg.Window("Combine AGS", layout = combine_layout, resizable = True, element_justification = "top")
    
    ### Step 6 - Event Loop: Where magic happens (or not)---------------------------
    while True:
        event, values = combine_ags_window.read()
        
        if event == None or event == 'OK': # if user closes window or clicks cancel
            break
            
        elif event == 'Add Files to Selection': # prompt the user to select xlsx files
            file_paths = sg.popup_get_file(message = "Select xlsx Files to Import...",no_window = True, file_types = (('Excel Files', '*.xlsx'),), multiple_files = True)
            file_path_accu = file_path_accu + list(file_paths)
            fnames_short = []
            for f in file_path_accu:
                fnames_short.append(os.path.basename(f)) # Getting a list of shortened file names (instead of full path) for display
            fnames_short = tuple(fnames_short)
            combine_ags_window["-EXCEL LIST-"].update(fnames_short) # Displays only the shortened filenames
            
        elif event == 'Clear File Selection': # Clears the list on display if the user wishes to re-select
            file_path_accu = []
            fnames_short = []
            file_paths = []
            combine_ags_window["-EXCEL LIST-"].update(fnames_short)
            
        elif event == 'Combine': # Starts the combine procedure ----------------------------------------Start of the heart of AGS_combiner!
            combine_ags_window["-STATUS TEXT-"].update("Status: Combining...")
            if len(values['-COMBINE-OUT-FDIR-']) != 0:                                    ## Check No.1: Checks if the user has specified output directory
                out_dir = values['-COMBINE-OUT-FDIR-']
                file_type_checksum = 0 
                for f in range(len(file_paths)): 
                    if (file_paths[f].endswith("xlsx"))|(file_paths[f].endswith("XLSX")): ## Check No.2: Checks if any selected file is not xlsx file
                        file_type_checksum += 1
                    else:
                        file_type_checksum = file_type_checksum
                if len(fnames_short) >= 1 and len(fnames_short) == file_type_checksum:
                    ### Step 7 Initializing the structure of the combined file
                    # Creates a master DataFrame, assigns the column headings and put information into it
                    df=pd.DataFrame(columns=['GIU_HOLE_ID','GIU_NO','HOLE_ID','DEPTH_FROM','DEPTH_TO','GEOL','GEOL_DESC','THICKNESS_M','TCR','RQD','WETH_GRAD','WETH','FI','Details'],index=[0])
                    row_index = 0  # Creates an accumulating index for recursive input to dataframe
                    if len(values["-GROUP LIST-"]) == 0:
                        group_list = ['HOLE']+['CORE', 'DETL', 'WETH', 'FRAC', 'GEOL']
                    else:
                        group_list = ['HOLE']+values["-GROUP LIST-"]
                    for f in range(len(file_paths)): # looping through the selected file list
#                         print("processing file: ",fnames_short[f]) # for debugging only
                        check_df = pd.read_excel(file_paths[f], sheet_name = 'PROJ')
                        if check_df.columns[0] == "AGS_FILE":                             ## Check No.3: Checks if the Excel file is from AGS_Excel function
                            check_df = pd.DataFrame()
                            ### Step 8: Read separate sheets for each file into a dictionary
                            group_dict = {}
                            for g in range(len(group_list)):
                                group_dict[group_list[g]] = pd.read_excel(file_paths[f], sheet_name = group_list[g])
                            GIU_HOLE_ID_list = group_dict['HOLE']['GIU_NO'].astype(str)+"_"+group_dict['HOLE']['HOLE_ID']
                            ### Step 9: Start adding data from each file recursively
                            for bh in range(len(GIU_HOLE_ID_list)):
                                GIU_NO_bh = group_dict['HOLE'].loc[bh,'GIU_NO']
                                HOLE_ID_bh = group_dict['HOLE'].loc[bh,'HOLE_ID']
                                #=====Step 9.1: getting combined from/to=====
                                # getting a sorted union of all depths from ONLY the selected groups
                                all_depths=[]
                                depth_from=[]
                                depth_to=[]
                                if 'CORE' in group_list:
                                    all_depths = all_depths + list(group_dict['CORE'][(group_dict['CORE']['HOLE_ID']==HOLE_ID_bh)&(group_dict['CORE']['GIU_NO']==GIU_NO_bh)]['CORE_TOP'].values)
                                    all_depths = all_depths + list(group_dict['CORE'][(group_dict['CORE']['HOLE_ID']==HOLE_ID_bh)&(group_dict['CORE']['GIU_NO']==GIU_NO_bh)]['CORE_BOT'].values)
                                if 'DETL' in group_list: 
                                    all_depths = all_depths + list(group_dict['DETL'][(group_dict['DETL']['HOLE_ID']==HOLE_ID_bh)&(group_dict['DETL']['GIU_NO']==GIU_NO_bh)]['DETL_TOP'].values)
                                    all_depths = all_depths + list(group_dict['DETL'][(group_dict['DETL']['HOLE_ID']==HOLE_ID_bh)&(group_dict['DETL']['GIU_NO']==GIU_NO_bh)]['DETL_BASE'].values)
                                if 'FRAC' in group_list: 
                                    all_depths = all_depths + list(group_dict['FRAC'][(group_dict['FRAC']['HOLE_ID']==HOLE_ID_bh)&(group_dict['FRAC']['GIU_NO']==GIU_NO_bh)]['FRAC_TOP'].values)
                                    all_depths = all_depths + list(group_dict['FRAC'][(group_dict['FRAC']['HOLE_ID']==HOLE_ID_bh)&(group_dict['FRAC']['GIU_NO']==GIU_NO_bh)]['FRAC_BASE'].values)
                                if 'GEOL' in group_list: 
                                    all_depths = all_depths + list(group_dict['GEOL'][(group_dict['GEOL']['HOLE_ID']==HOLE_ID_bh)&(group_dict['GEOL']['GIU_NO']==GIU_NO_bh)]['GEOL_TOP'].values)
                                    all_depths = all_depths + list(group_dict['GEOL'][(group_dict['GEOL']['HOLE_ID']==HOLE_ID_bh)&(group_dict['GEOL']['GIU_NO']==GIU_NO_bh)]['GEOL_BASE'].values)
                                if 'WETH' in group_list: 
                                    all_depths = all_depths + list(group_dict['WETH'][(group_dict['WETH']['HOLE_ID']==HOLE_ID_bh)&(group_dict['WETH']['GIU_NO']==GIU_NO_bh)]['WETH_TOP'].values)
                                    all_depths = all_depths + list(group_dict['WETH'][(group_dict['WETH']['HOLE_ID']==HOLE_ID_bh)&(group_dict['WETH']['GIU_NO']==GIU_NO_bh)]['WETH_BASE'].values)
                                depths=list(set().union(all_depths))
                                depths.sort()
                                depth = [x for x in depths if str(x) != 'nan']   # Removes NaN values from the sorted depths list
                                depth.sort()
                                # creating a "from and to" from this list
                                depth_from=depth[0:-1]
                                depth_to=depth[1:]

                                #=====Step 9.2: filling in data into the dataframe=====
                                #filling the from/to into the master DF
                                d = 0
                                for d in range(len(depth_to)):
                                    df.loc[row_index,'GIU_HOLE_ID'] = GIU_HOLE_ID_list[bh]
                                    df.loc[row_index,'GIU_NO'] = GIU_NO_bh
                                    df.loc[row_index,'HOLE_ID'] = HOLE_ID_bh
                                    df.loc[row_index,'DEPTH_FROM'] = depth_from[d]
                                    df.loc[row_index,'DEPTH_TO'] = depth_to[d]
                                    df.loc[row_index,'THICKNESS_M'] = depth_to[d]-depth_from[d]
                                    row_index=row_index+1       

                                #filling from CORE sheet
                                if 'CORE' in group_list:
                                    core = group_dict['CORE'].loc[(group_dict['CORE']['HOLE_ID']==HOLE_ID_bh)&(group_dict['CORE']['GIU_NO']==GIU_NO_bh)]
                                    for c in range(0,len(list(group_dict['CORE'][group_dict['CORE']['HOLE_ID']==HOLE_ID_bh]['CORE_TOP']))):
                                        df.loc[(df.HOLE_ID==HOLE_ID_bh)&(df.GIU_NO==GIU_NO_bh)&(df.DEPTH_FROM.between(core.iloc[c]['CORE_TOP'],core.iloc[c]['CORE_BOT'], inclusive = 'left')),
                                               'RQD'] = core.iloc[c]['CORE_RQD']
                                        df.loc[(df.HOLE_ID==HOLE_ID_bh)&(df.GIU_NO==GIU_NO_bh)&(df.DEPTH_FROM.between(core.iloc[c]['CORE_TOP'],core.iloc[c]['CORE_BOT'], inclusive = 'left')),
                                               'TCR'] = core.iloc[c]['CORE_PREC']

                                #filling from DETL sheet
                                if 'DETL' in group_list:
                                    detl = group_dict['DETL'].loc[(group_dict['DETL']['HOLE_ID']==HOLE_ID_bh)&(group_dict['DETL']['GIU_NO']==GIU_NO_bh)]
                                    for d in range(0,len(list(group_dict['DETL'][group_dict['DETL']['HOLE_ID']==HOLE_ID_bh]['DETL_TOP']))):
    #                                     detl = DETL.loc[(DETL['HOLE_ID']== HOLE_ID_bh)]
                                        df.loc[(df.HOLE_ID==HOLE_ID_bh)&(df.GIU_NO==GIU_NO_bh)&(df.DEPTH_FROM.between(detl.iloc[d]['DETL_TOP'],detl.iloc[d]['DETL_BASE'], inclusive = 'left')),
                                               'Details'] = detl.iloc[d]['DETL_DESC']

                                #filling from FRAC sheet
                                if 'FRAC' in group_list:
                                    frac = group_dict['FRAC'].loc[(group_dict['FRAC']['HOLE_ID']==HOLE_ID_bh)&(group_dict['FRAC']['GIU_NO']==GIU_NO_bh)]                
                                    for fr in range(1,len(list(group_dict['FRAC'][group_dict['FRAC']['HOLE_ID']==HOLE_ID_bh]['FRAC_TOP']))):
    #                                     frac = FRAC.loc[(FRAC['HOLE_ID']== HOLE_ID_bh)]
                                        df.loc[(df.HOLE_ID==HOLE_ID_bh)&(df.GIU_NO==GIU_NO_bh)&(df.DEPTH_FROM.between(frac.iloc[fr]['FRAC_TOP'],frac.iloc[fr]['FRAC_BASE'], inclusive = 'left')),
                                               'FI'] = frac.iloc[fr]['FRAC_FI']

                                #filling from GEOL sheet
                                if 'GEOL' in group_list:
                                    geol = group_dict['GEOL'].loc[(group_dict['GEOL']['HOLE_ID']==HOLE_ID_bh)&(group_dict['GEOL']['GIU_NO']==GIU_NO_bh)]    
                                    for g in range(0,len(list(group_dict['GEOL'][group_dict['GEOL']['HOLE_ID']==HOLE_ID_bh]['GEOL_TOP']))):
    #                                     geol = GEOL.loc[(GEOL['HOLE_ID']== HOLE_ID_bh)]
                                        df.loc[(df.HOLE_ID==HOLE_ID_bh)&(df.GIU_NO==GIU_NO_bh)&(df.DEPTH_FROM.between(geol.iloc[g]['GEOL_TOP'],geol.iloc[g]['GEOL_BASE'], inclusive = 'left')),
                                               'GEOL'] = geol.iloc[g]['GEOL_LEG']
                                        df.loc[(df.HOLE_ID==HOLE_ID_bh)&(df.GIU_NO==GIU_NO_bh)&(df.DEPTH_FROM.between(geol.iloc[g]['GEOL_TOP'],geol.iloc[g]['GEOL_BASE'], inclusive = 'left')),
                                               'GEOL_DESC'] = geol.iloc[g]['GEOL_DESC']

                                #filling from WETH sheet
                                if 'WETH' in group_list:
                                    weth = group_dict['WETH'].loc[(group_dict['WETH']['HOLE_ID']==HOLE_ID_bh)&(group_dict['WETH']['GIU_NO']==GIU_NO_bh)] 
                                    for w in range(0,len(list(group_dict['WETH'][group_dict['WETH']['HOLE_ID']==HOLE_ID_bh]['WETH_TOP']))):
    #                                     weth = WETH.loc[(WETH['HOLE_ID']== HOLE_ID_bh)]
                                        df.loc[(df.HOLE_ID==HOLE_ID_bh)&(df.GIU_NO==GIU_NO_bh)&(df.DEPTH_FROM.between(weth.iloc[w]['WETH_TOP'],weth.iloc[w]['WETH_BASE'], inclusive = 'left')),
                                               'WETH_GRAD'] = weth.iloc[w]['WETH_GRAD']
                                    # Adding a column for slash weathering grade cases. WETH_GRAD preserves original, WETH shows simplified (on conservative side) weathering grades.
                                    df['WETH'] = df['WETH_GRAD']
                                    df.loc[(df.WETH_GRAD=='I/II')|(df.WETH_GRAD=='II/I'),'WETH'] = 'II'
                                    df.loc[(df.WETH_GRAD=='II/III')|(df.WETH_GRAD=='III/II'),'WETH'] = 'III'
                                    df.loc[(df.WETH_GRAD=='III/IV')|(df.WETH_GRAD=='IV/III')|(df.WETH_GRAD.str.contains('III')&df.WETH_GRAD.str.contains('IV')),'WETH'] = 'IV'
                                    df.loc[(df.WETH_GRAD=='IV/V')|(df.WETH_GRAD=='V/IV'),'WETH'] = 'V'
                                    df.loc[(df.WETH_GRAD=='V/VI')|(df.WETH_GRAD=='VI/V'),'WETH'] = 'VI' ### How often does this case occur? Should it really be interpreted like so?
                        else: # Exit if Check No.3 is not passed
                            sg.popup("Current version only supports Excel files from AGS to Excel function.", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
                            break
                            combine_ags_window["-STATUS TEXT-"].update("Status: Idle")
                    df.to_excel(out_dir)
                    sg.popup("Combining Complete. Please double check.", title = "Congratulations!", font = default_font, auto_close = True, auto_close_duration = 15,)
                    combine_ags_window["-STATUS TEXT-"].update("Status: Idle")
                elif len(fnames_short) != file_type_checksum: # Exit if Check No.1 is not passed
                    sg.popup("At least one file selected is not xlsx file. Please double check.", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
                    combine_ags_window["-STATUS TEXT-"].update("Status: Idle")
                else: # Exit if no files are selected
                    sg.popup("Please select at least one xlsx file!", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
                    combine_ags_window["-STATUS TEXT-"].update("Status: Idle")
            else:
                sg.popup("Please specify output directory!", font = default_font, title = "Sorry!", auto_close = True, auto_close_duration = 15,)
                combine_ags_window["-STATUS TEXT-"].update("Status: Idle")
    ### Step 7 - Close your window when break out of while loop!--------------------        
    combine_ags_window.close()