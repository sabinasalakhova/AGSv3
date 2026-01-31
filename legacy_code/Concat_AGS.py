### Step 1 Import and Initialize---------------------------------------
import PySimpleGUI as sg
import os.path
import numpy as np
import pandas as pd

def Concat_AGS(file_paths):
    """
    Concatenate and read AGS file(s) selectively and output the result to an Excel file.
    
    Called by: 
    -AGS_Excel
    
    Dependent functions:
    -is_file_like
    -AGS4_to_dict
    -AGS4_to_dataframe
    -AGS4_to_excel
    
    Supports reading files in different directories.
    
    Inputs:
    file_paths: PATHS of files to concatenate.
    
    User inputs prompted:
    -GIU No.: Assign (unique) number for ease of refernce for cases with duplicate BH names (e.g. DH1)
    -Hole types to ignore
    -Path to save as
    
    Exceptions handled:
    -?ETH case
    combining ?LEGD and LEGD case
    ?HORN group
    ? in column names (deleted and retained last string behind ?)
    
    Outputs:
    Excel with concatenated ags files.
    """
    # Adding a touch of color
    sg.theme('DarkGreen') 
    default_font = 'Calibri 10'
    table_font = 'Calibri 8'
    
    num_files = len(file_paths)
#     print(num_files) ## for debugging only. Shows the number of files passed in
    ### Step 0.1: Checks whether the files are in the same directory (commented out since new version already supports reading in multiple directory)
    # f_dir = os.path.dirname(file_paths[0])
    # for p in range(len(file_paths)):
    #     if os.path.dirname(file_paths[p]) == f_dir:
    #         pass
    #     else:
    #         sg.popup("Current version only supports files in the same directory.", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
    #         break
    ### Step 0.2: Checks whether the files exist
    for p in range(len(file_paths)):
        if os.path.exists(os.path.dirname(file_paths[p])):
            pass
        else:
            sg.popup("At least 1 of the selected file(s) do(es) not exist!", title = "Sorry!", font = default_font, auto_close = True, auto_close_duration = 15,)
            break
    ### Getting file names:
    file_names = []
    for p in range(len(file_paths)):
        file_names.append(os.path.basename(file_paths[p]))

    ### Step 1: Dependent functions
    ## is_file_like from python_ags4----------------------------------------------
    def is_file_like(obj):
        """
        Check if object is file like.
        Returns
        -------
        bool
            Return True if obj is file like, otherwise return False
        """

        if not (hasattr(obj, 'read') or hasattr(obj, 'write')):
            return False

        if not hasattr(obj, "__iter__"):
            return False

        return True

    ## AGS_4_to_dict from python ags4---------------------------------------------
    def AGS4_to_dict(filepath_or_buffer, encoding='utf-8'):
        """
        Credits: Python AGS4 package
        Load all the data in a AGS file to a dictionary of dictionaries.
        This GROUP in the AGS4 file is assigned its own dictionary.

        'AGS4_to_dataframe' uses this funtion to load AGS4 data in to Pandas
        dataframes.

        Parameters
        ----------
        filepath_or_buffer : File path (str, pathlib.Path), or StringIO.
            Path to AGS4 file or any object with a read() method (such as an open file or StringIO).

        Returns
        -------
        data : dict
            Python dictionary populated with data from the AGS4 file with AGS4 headers as keys
        headings : dict
            Dictionary with the headings in the each GROUP (This will be needed to
            recall the correct column order when writing pandas dataframes back to AGS4
            files. i.e. input for 'dataframe_to_AGS4()' function)
        """

        if is_file_like(filepath_or_buffer):
            f = filepath_or_buffer
            close_file = False
        else:
            # Read file with errors="replace" to catch UnicodeDecodeErrors
            f = open(filepath_or_buffer, "r", encoding=encoding, errors="replace")
            close_file = True

        try:
            data = {}

            # dict to save and output the headings. This is not really necessary
            # for the read AGS4 function but will be needed to write the columns
            # of pandas dataframes when writing them back to AGS4 files.
            # (The HEADING column needs to be the first column in order to preserve
            # the AGS data format. Other columns in certain groups have a
            # preferred order as well)

            headings = {}

            for i, line in enumerate(f, start=1):
                temp = line.rstrip().split('","')
                temp = [item.strip('"') for item in temp]

                if '**' in temp[0]: # GROUP
                    row = 0
                    group = temp[0][2:]
                    data[group] = {}

                elif '*' in temp[0]: # HEADING
                    row += 1
                    cleaned_headings = [item[1:] for item in temp]

                    if row==1:
                        headings[group] = cleaned_headings

                    # for the exceptions where the columns are split into different rows
                    else: 
                        headings[group].extend(cleaned_headings)

                    ## Catch duplicate headings
                    try:
                        assert len(headings[group])==len(set(headings[group]))
                    except AssertionError:
                        item_count = {}

                        for i, item in enumerate(headings[group]):
                            if item not in item_count:
                                item_count[item] = {'i': i, 'count': 0}
                            else:
                                item_count[item]['i'] = i
                                item_count[item]['count'] += 1

                                headings[group][i] = headings[group][i]+'_'+str(item_count[item]['count'])

                    for item in headings[group]:
                        data[group][item] = []

                elif '<CONT>' in temp[0]:
                    # for the exceptions where the columns are split into 
                    # different rows
                    for i in range(1, len(temp)):
                        data[group][headings[group][i]][-1] += temp[i]

                elif len(temp[0])==0 and len(temp)==1: # GROUP BREAKS
                    continue

                else: # DATA / UNITS
                    for i in range(len(temp)):
                        data[group][headings[group][i]].append(temp[i])

        finally:
            if close_file:
                f.close()

        return data, headings

    ## AGS4_to_dataframe from python ags4-----------------------------------------
    def AGS4_to_dataframe(filepath_or_buffer, encoding='utf-8'):
        """
        Load all the tables in a AGS4 file to a Pandas dataframes. The output is
        a Python dictionary of dataframes with the name of each AGS4 table (i.e.
        GROUP) as the primary key.

        Parameters
        ----------
        filepath_or_buffer : str, StringIO
            Path to AGS4 file or any file like object (open file or StringIO)

        Returns
        -------
        data : dict
            Python dictionary populated with Pandas dataframes. Each GROUP in the AGS4 files is assigned to its a dataframe.
        headings : dict
            Dictionary with the headings in the each GROUP (This will be needed to
            recall the correct column order when writing pandas dataframes back to AGS4
            files. i.e. input for 'dataframe_to_AGS4()' function)
        """

        from pandas import DataFrame

        # Extract AGS4 file into a dictionary of dictionaries
        data, headings = AGS4_to_dict(filepath_or_buffer, encoding=encoding)

        # Convert dictionary of dictionaries to a dictionary of Pandas dataframes
        df = {}
        for key in data:
            try:
                table = DataFrame(data[key])
                table[1:] = table[1:].apply(pd.to_numeric, errors='ignore')
                df[key] = table
            except ValueError:
                print ('check file: {} is not exported'.format(key))
                continue
        return df, headings
    
    ## AGS4_to_excel from python ags4---------------------------------------------
    def AGS4_to_excel(input_file, output_file, encoding='utf-8'):
        """Load all the tables in a AGS4 file to an Excel spreasheet.

        Parameters
        ----------
        input_file : str
            Path to AGS4 file
        output_file : str
            Path to Excel file

        Returns
        -------
        Excel file populated with data from the input AGS4 file.
        """

        from pandas import ExcelWriter

        # Extract AGS4 file into a dictionary of dictionaries
        tables, headings = AGS4_to_dataframe(input_file, encoding=encoding)

        # Write to Excel file
        with ExcelWriter(output_file) as writer:
            for key in tables:
                try:
                    new_key = key
                    if '?' in key:
                        new_key = new_key.replace('?', '_')
                    tables[key].to_excel(writer, sheet_name=new_key, index=False)
                except ValueError:
                    print ('Not printed:', key)
                    
    ### Step 2: Setting up a group list for later reference.
    group_list = ['PROJ', 'HOLE', 'GEOL', 'WETH', 'CORE', 'FRAC', 'DETL', 'ISPT', 'SAMP', 'LEGD', 'DISC', 'PTIM', 'HORN',
                  'ABBR', 'CDIA', 'CLSS', 'CNMT', 'CODE', 'DICT', 'DPRB', 'DPRG', 'DREM', 'FLSH', 'GRAD', 'HDIA', 
                  'IDEN', 'IPRM', 'IVAN', 'POBS', 'PREF', 'PRTD', 'PRTG', 'PRTL', 'ROCK', 'SHBG', 'SHBT', 'TRIG', 'TRIX', 'UNIT']

    ### Step 3: Defining the "main" layout of the popup    
    concat_layout = [
        [
            sg.Text("Please input the respective GIU Nos.: ",font = default_font),
        ],
        *[
            [sg.Text(str(file_names[i])+": ",font = default_font),sg.Push(),sg.Input(key='_IN'+str(i)+'_'),]for i in range(num_files)
        ],
        [
            sg.Push(),
            sg.Button("Assign GIU No.",pad=(5,5),font = default_font, size = (12,1))
        ],
        [
            [sg.Text(" ", key = '_GIUText'+str(i)+'_',font = default_font)]for i in range(num_files)
        ],
        [
            sg.Text("Click to highlight and ignore hole types from this list: ", font = default_font),
            sg.Listbox(
                values = ["TP", "GCOP", "IP", "CH", "VC", "ICH", "ROTARY", "Any hole type that contains 'RC'",],
                select_mode = sg.LISTBOX_SELECT_MODE_MULTIPLE,
                enable_events=True,
                size = (30,9),
                key="_IGNORE LIST_",
                no_scrollbar = False,
                expand_x = True,
                expand_y = True,
            )
        ],
        [
            sg.Text("Save as Excel File: ", font = default_font),
            sg.Input(size=(50,1), font = default_font, key = '_CONCAT_OUT_FDIR_'),
            sg.FileSaveAs(button_text = "Browse...", target = '_CONCAT_OUT_FDIR_', file_types = (('Excel Files', '*.xlsx'),), pad=(5,5),font = default_font),
        ],
        [
            sg.Push(),
            sg.Button("Concatenate",pad=(5,5),font = default_font, size = (12,1))
        ],
    ]
    ### Step 4 - Creating Window----------------------------------------------------
    concat_ags_window = sg.Window("Concat AGS", layout = concat_layout, resizable = True, element_justification = "top")
    
     ### Step 5 - Event Loop: Where magic happens (or not)---------------------------
    while True:
        event, values = concat_ags_window.read()
        if event == None or event == 'OK': # if user closes window or clicks cancel
            break
        elif event == 'Assign GIU No.': # Update the UI after user input GIU numbers
            for i in range(num_files):
                concat_ags_window['_GIUText'+str(i)+'_'].update("The file "+file_names[i]+" has been assigned a GIU No. of "+values['_IN'+str(i)+'_']+".")
        elif event == 'Concatenate':  # Steps for actually concatenating
            # checks if output directory is sepcified
            if len(values['_CONCAT_OUT_FDIR_']) == 0:
                sg.popup("Please specify output directory!", title = "Sorry!", auto_close = True, auto_close_duration = 15,)
                break
            else:
                out_dir = values['_CONCAT_OUT_FDIR_']
            for i in range(num_files):
                # checks and breaks the for loop if any one of the ags file has not been assigned a GIU no.
                if len(values['_IN'+str(i)+'_']) == 0:
                    sg.popup("Please assign a unique GIU No. for each AGS file to avoid clashing of data!", title = "Sorry!", auto_close = True, auto_close_duration = 15,)
                    break
                df , headings = AGS4_to_dataframe(file_paths[i]) # Reads the ags file into a dictionary of dataframes
                    # Handles exceptions where <UNITS> is present, or group names are invalid
                for d in list(df):
                    if (df[d].iloc[0,0] == "<UNIT>") | (df[d].iloc[0,0] == "<UNITS>"):
                        df[d] = df[d].drop([0])
                        df[d].columns = [c.split("?")[-1] if "?" in c else c for c in df[d].columns] # Handles cases where "?" appears in column names
                    if d == "?ETH":
                        df["WETH"] = df.pop("?ETH")
                        headings["WETH"] = headings.pop("?ETH")
                    elif d == "?LEGD":
                        df["LEGD"] = df.pop("?LEGD")
                        headings["LEGD"] = headings.pop("?LEGD")
                    elif d == "?HORN":
                        df["HORN"] = df.pop("?HORN")
                        headings["HORN"] = headings.pop("?HORN")
                # Handles exceptions where groups are missing
                for group in group_list:
                    if group not in df.keys():
                        headings[group] = pd.DataFrame()
                        df[group] = pd.DataFrame({"HOLE_ID":[]})
                # Checks and deletes if any boreholes are in the -IGNORE LIST-
                if "Any hole type that contains 'RC'" not in values["_IGNORE LIST_"]:
                    ignore_holes = df['HOLE'].loc[(df['HOLE']['HOLE_TYPE'].isin(values["_IGNORE LIST_"]))].HOLE_ID
                    for d in list(df):
                        try:
                            df[d] = df[d].loc[~(df[d]['HOLE_ID'].isin(ignore_holes)),:]
                        except KeyError:
                            pass
                else:
                    ignore_holes = df['HOLE'].loc[(df['HOLE']['HOLE_TYPE'].isin(values["_IGNORE LIST_"]))|(df['HOLE']['HOLE_TYPE'].str.contains("RC"))].HOLE_ID
                    for d in list(df):
                        try:
                            df[d] = df[d].loc[~(df[d]['HOLE_ID'].isin(ignore_holes)),:]
                        except KeyError:
                            pass
                # Inserts the columns of GIU No and AGS file name according to user input
                for d in list(df):
                    df[d].insert(loc=0, column = 'GIU_NO', value = values['_IN'+str(i)+'_'])
                df['PROJ'].insert(loc=0, column = 'AGS_FILE', value = os.path.basename(file_paths[i]))
                if i == 0: # Copies from df for the first time in the loop
                    concat_df = df
                    concat_headings = headings
                else:      # Use pandas concat method to join the Dataframes together
                    for d in list(df):
                        concat_df[d] = pd.concat([concat_df[d],df[d]], ignore_index = True)
            # Writes the actual excel file
            with pd.ExcelWriter(out_dir) as writer:
                for key in list(concat_df):
                    try:
                        new_key = key
                        if '?' in key:
                            new_key = new_key.replace('?', '_')
                        concat_df[key].to_excel(writer, sheet_name=new_key, index=False)
                    except ValueError:
                         print ('Not printed:', key) 
    ### Step 7 - Close your window when break out of while loop!--------------------        
    concat_ags_window.close()