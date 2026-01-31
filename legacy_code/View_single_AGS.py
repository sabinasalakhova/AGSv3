### Step 1 Import and Initialize---------------------------------------
import PySimpleGUI as sg
import os.path
import numpy as np
import pandas as pd

def View_single_AGS(file_path):
    """
    Views an AGS file in a popup window.
    Called by AGS_Excel.
    Dependent functions:
    -is_file_like
    -AGS4_to_dict
    -AGS4_to_dataframe
    
    Inputs:
    file_path: path of AGS (*.ags)file.
    
    Exceptions handled:
    ?ETH case
    combining ?LEGD and LEGD case
    ?HORN group
    
    """
    ### Step 0: Separates (again) the directory and file name
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    # Adding a touch of color
    sg.theme('DarkGreen') 
    default_font = 'Calibri 10'
    table_font = 'Calibri 8'
    
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
    
    
    ### Step 2: Reading the ags file into a dictionary.
    df , headings = AGS4_to_dataframe(file_path)
    # Handles except where group names are invalid (Known exceptions ONLY!)
    group_list = ['PROJ', 'HOLE', 'GEOL', 'WETH', 'CORE', 'FRAC', 'DETL', 'ISPT', 'SAMP', 'LEGD', 'DISC', 'PTIM', 'HORN',
                  'ABBR', 'CDIA', 'CLSS', 'CNMT', 'CODE', 'DICT', 'DPRB', 'DPRG', 'DREM', 'FLSH', 'GRAD', 'HDIA', 
                  'IDEN', 'IPRM', 'IVAN', 'POBS', 'PREF', 'PRTD', 'PRTG', 'PRTL', 'ROCK', 'SHBG', 'SHBT', 'TRIG', 'TRIX', 'UNIT']
    for d in list(df):
        if d == "?ETH":
            df["WETH"] = df.pop("?ETH")
            headings["WETH"] = headings.pop("?ETH")
        elif d == "?LEGD":
            df["LEGD"] = df.pop("?LEGD")
            headings["LEGD"] = headings.pop("?LEGD")
        elif d == "?HORN":
            df["HORN"] = df.pop("?HORN")
            headings["HORN"] = headings.pop("?HORN")
    # Handles exceptions where group is missing
    for group in group_list:
        if group not in df.keys():
            headings[group] = pd.DataFrame()
            df[group] = pd.DataFrame({"HOLE_ID":[]})

    ### Step 3: Defining individual layouts in the tabs
    PROJ_layout = [
        [
            sg.Table(
            values = df['PROJ'].values.tolist(),
            headings = headings['PROJ'],
            num_rows = 20,
            key = '-PROJ-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    HOLE_layout = [
        [
            sg.Table(
            values = df['HOLE'].values.tolist(),
            headings = headings['HOLE'],
            num_rows = 20,
            key = '-HOLE-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    GEOL_layout = [
        [
            sg.Table(
            values = df['GEOL'].values.tolist(),
            headings = headings['GEOL'],
            num_rows = 20,
            key = '-GEOL-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    WETH_layout = [
        [
            sg.Table(
            values = df['WETH'].values.tolist(),
            headings = headings['WETH'],
            num_rows = 20,
            key = '-WETH-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    CORE_layout = [
        [
            sg.Table(
            values = df['CORE'].values.tolist(),
            headings = headings['CORE'],
            num_rows = 20,
            key = '-CORE-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]    
    FRAC_layout = [
        [
            sg.Table(
            values = df['FRAC'].values.tolist(),
            headings = headings['FRAC'],
            num_rows = 20,
            key = '-FRAC-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    DETL_layout = [
        [
            sg.Table(
            values = df['DETL'].values.tolist(),
            headings = headings['DETL'],
            num_rows = 20,
            key = '-DETL-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    ISPT_layout = [
        [
            sg.Table(
            values = df['ISPT'].values.tolist(),
            headings = headings['ISPT'],
            num_rows = 20,
            key = '-ISPT-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3', 
            expand_x = True,
            expand_y = True,),
        ]
    ]
    SAMP_layout = [
        [
            sg.Table(
            values = df['SAMP'].values.tolist(),
            headings = headings['SAMP'],
            num_rows = 20,
            key = '-SAMP-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    LEGD_layout = [
        [
            sg.Table(
            values = df['LEGD'].values.tolist(),
            headings = headings['LEGD'],
            num_rows = 20,
            key = '-LEGD-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    DISC_layout = [
        [
            sg.Table(
            values = df['DISC'].values.tolist(),
            headings = headings['DISC'],
            num_rows = 20,
            key = '-DISC-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    PTIM_layout = [
        [
            sg.Table(
            values = df['PTIM'].values.tolist(),
            headings = headings['PTIM'],
            num_rows = 20,
            key = '-PTIM-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    HORN_layout = [
        [
            sg.Table(
            values = df['HORN'].values.tolist(),
            headings = headings['HORN'],
            num_rows = 20,
            key = '-HORN-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]    
    ABBR_layout = [
        [
            sg.Table(
            values = df['ABBR'].values.tolist(),
            headings = headings['ABBR'],
            num_rows = 20,
            key = '-ABBR-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    CDIA_layout = [
        [
            sg.Table(
            values = df['CDIA'].values.tolist(),
            headings = headings['CDIA'],
            num_rows = 20,
            key = '-CDIA-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    CLSS_layout = [
        [
            sg.Table(
            values = df['CLSS'].values.tolist(),
            headings = headings['CLSS'],
            num_rows = 20,
            key = '-CLSS-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    CNMT_layout = [
        [
            sg.Table(
            values = df['CNMT'].values.tolist(),
            headings = headings['CNMT'],
            num_rows = 20,
            key = '-CNMT-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    CODE_layout = [
        [
            sg.Table(
            values = df['CODE'].values.tolist(),
            headings = headings['CODE'],
            num_rows = 20,
            key = '-CODE-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    DICT_layout = [
        [
            sg.Table(
            values = df['DICT'].values.tolist(),
            headings = headings['DICT'],
            num_rows = 20,
            key = '-DICT-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    DPRB_layout = [
        [
            sg.Table(
            values = df['DPRB'].values.tolist(),
            headings = headings['DPRB'],
            num_rows = 20,
            key = '-DPRB-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    DPRG_layout = [
        [
            sg.Table(
            values = df['DPRG'].values.tolist(),
            headings = headings['DPRG'],
            num_rows = 20,
            key = '-DPRG-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    DREM_layout = [
        [
            sg.Table(
            values = df['DREM'].values.tolist(),
            headings = headings['DREM'],
            num_rows = 20,
            key = '-DREM-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    FLSH_layout = [
        [
            sg.Table(
            values = df['FLSH'].values.tolist(),
            headings = headings['FLSH'],
            num_rows = 20,
            key = '-FLSH-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    GRAD_layout = [
        [
            sg.Table(
            values = df['GRAD'].values.tolist(),
            headings = headings['GRAD'],
            num_rows = 20,
            key = '-GRAD-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    HDIA_layout = [
        [
            sg.Table(
            values = df['HDIA'].values.tolist(),
            headings = headings['HDIA'],
            num_rows = 20,
            key = '-HDIA-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    IDEN_layout = [
        [
            sg.Table(
            values = df['IDEN'].values.tolist(),
            headings = headings['IDEN'],
            num_rows = 20,
            key = '-IDEN-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    IPRM_layout = [
        [
            sg.Table(
            values = df['IPRM'].values.tolist(),
            headings = headings['IPRM'],
            num_rows = 20,
            key = '-IPRM-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    IVAN_layout = [
        [
            sg.Table(
            values = df['IVAN'].values.tolist(),
            headings = headings['IVAN'],
            num_rows = 20,
            key = '-IVAN-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    POBS_layout = [
        [
            sg.Table(
            values = df['POBS'].values.tolist(),
            headings = headings['POBS'],
            num_rows = 20,
            key = '-POBS-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    PREF_layout = [
        [
            sg.Table(
            values = df['PREF'].values.tolist(),
            headings = headings['PREF'],
            num_rows = 20,
            key = '-PREF-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    PRTD_layout = [
        [
            sg.Table(
            values = df['PRTD'].values.tolist(),
            headings = headings['PRTD'],
            num_rows = 20,
            key = '-PRTD-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    PRTG_layout = [
        [
            sg.Table(
            values = df['PRTG'].values.tolist(),
            headings = headings['PRTG'],
            num_rows = 20,
            key = '-PRTG-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    PRTL_layout = [
        [
            sg.Table(
            values = df['PRTL'].values.tolist(),
            headings = headings['PRTL'],
            num_rows = 20,
            key = '-PRTL-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    ROCK_layout = [
        [
            sg.Table(
            values = df['ROCK'].values.tolist(),
            headings = headings['ROCK'],
            num_rows = 20,
            key = '-ROCK-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    SHBG_layout = [
        [
            sg.Table(
            values = df['SHBG'].values.tolist(),
            headings = headings['SHBG'],
            num_rows = 20,
            key = '-SHBG-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    SHBT_layout = [
        [
            sg.Table(
            values = df['SHBT'].values.tolist(),
            headings = headings['SHBT'],
            num_rows = 20,
            key = '-SHBT-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    TRIG_layout = [
        [
            sg.Table(
            values = df['TRIG'].values.tolist(),
            headings = headings['TRIG'],
            num_rows = 20,
            key = '-TRIG-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    TRIX_layout = [
        [
            sg.Table(
            values = df['TRIX'].values.tolist(),
            headings = headings['TRIX'],
            num_rows = 20,
            key = '-TRIX-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    UNIT_layout = [
        [
            sg.Table(
            values = df['UNIT'].values.tolist(),
            headings = headings['UNIT'],
            num_rows = 20,
            key = '-UNIT-TABLE-',
            enable_events = True,
            font = table_font,
            row_height = 15,
            header_background_color = 'OliveDrab4',
            header_text_color = 'White',
            background_color = 'DarkOliveGreen1',
            alternating_row_color = 'DarkOliveGreen3',
            expand_x = True,
            expand_y = True,),
        ]
    ]
    
    ### Step 4: Defining the "main" layout of the popup    
    pop_layout = [
        [
            sg.Text("Viewing: "+file_name,font = default_font),
        ],
        [
            sg.TabGroup(
            [[
                sg.Tab('PROJ',PROJ_layout,font = default_font),
                sg.Tab('HOLE',HOLE_layout,font = default_font),
                sg.Tab('GEOL',GEOL_layout,font = default_font),
                sg.Tab('WETH',WETH_layout,font = default_font),
                sg.Tab('CORE',CORE_layout,font = default_font),
                sg.Tab('FRAC',FRAC_layout,font = default_font),
                sg.Tab('DETL',DETL_layout,font = default_font),
                sg.Tab('ISPT',ISPT_layout,font = default_font),
                sg.Tab('SAMP',SAMP_layout,font = default_font),
                sg.Tab('LEGD',LEGD_layout,font = default_font),
                sg.Tab('DISC',DISC_layout,font = default_font),
                sg.Tab('PTIM',PTIM_layout,font = default_font),
                sg.Tab('HORN',HORN_layout,font = default_font),
                sg.Tab('ABBR',ABBR_layout,font = default_font),
                sg.Tab('CDIA',CDIA_layout,font = default_font),
                sg.Tab('CLSS',CLSS_layout,font = default_font),
                sg.Tab('CNMT',CNMT_layout,font = default_font),
                sg.Tab('CODE',CODE_layout,font = default_font),
                sg.Tab('DICT',DICT_layout,font = default_font),
                sg.Tab('DPRB',DPRB_layout,font = default_font),
                sg.Tab('DPRG',DPRG_layout,font = default_font),
                sg.Tab('DREM',DREM_layout,font = default_font),
                sg.Tab('FLSH',FLSH_layout,font = default_font),
                sg.Tab('GRAD',GRAD_layout,font = default_font),
                sg.Tab('HDIA',HDIA_layout,font = default_font), 
                sg.Tab('IDEN',IDEN_layout,font = default_font),
                sg.Tab('IPRM',IPRM_layout,font = default_font),
                sg.Tab('IVAN',IVAN_layout,font = default_font),
                sg.Tab('POBS',POBS_layout,font = default_font),
                sg.Tab('PREF',PREF_layout,font = default_font),
                sg.Tab('PRTD',PRTD_layout,font = default_font),
                sg.Tab('PRTG',PRTG_layout,font = default_font),
                sg.Tab('PRTL',PRTL_layout,font = default_font),
                sg.Tab('ROCK',ROCK_layout,font = default_font),
                sg.Tab('SHBG',SHBG_layout,font = default_font),
                sg.Tab('SHBT',SHBT_layout,font = default_font),
                sg.Tab('TRIG',TRIG_layout,font = default_font),
                sg.Tab('TRIX',TRIX_layout,font = default_font),
                sg.Tab('UNIT',UNIT_layout,font = default_font),
            ]],
            tab_location = 'bottomleft',),
        ],
        [
            sg.Push(),
            sg.Button("OK",pad=(5,5),font = default_font, size = (12,1)),
        ],
    ]
    ### Step 5 - Creating Window----------------------------------------------------
    view_ags_window = sg.Window("AGS Viewer", layout = pop_layout, size = (1650, 500),resizable = True, element_justification = "top")
    
    ### Step 6 - Event Loop: Where magic happens (or not)---------------------------
    while True:
        event, values = view_ags_window.read()
        if event == None or event == 'OK': # if user closes window or clicks cancel
            break
            
    ### Step 7 - Close your window when break out of while loop!--------------------        
    view_ags_window.close()