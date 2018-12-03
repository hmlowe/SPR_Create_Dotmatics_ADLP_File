from glob import glob
import os
import pandas as pd



def dup_item_for_dot_df(df, col_name, times_dup=3, sort=False):
    """
    Takes a DataFrame and a column name with items to be replicated. Sorts the list and replicates the number of
    times specified by the parameter times_dup. Copies the replicated values to the clip board.

    :param df: A DataFrame containing the column of values to be replicated.
    :param col_name: Name of the column containing values to replicate.
    :param times_dup: Number of times to replicate each value in the specified column.
    :param sort: Boolean to sort the replicated values.
    :type sort: bool
    """
    dup_list = []

    try:
        for item in df[col_name]:
            for i in range(times_dup):
                dup_list.append(item)

        a = pd.Series(dup_list)

        if sort:
            b = a.sort_values()
            return b
        else:
            return a
    except:
        print("The DataFrame does not have a " + col_name + " column.")


def spr_image_file_list_from_folder(path_ss_img):
    """
    This method takes a list path to an SPR image file folder as an argument and returns a list of tuples of all the
    image names in the correct order.

    Note that image files in the folder must be named as follows:
    'BRD-0629_4_181029_results_affinity_1.png'

    :param path_ss_img: Directory path to the folder containing the images.
    :return: List of Tuples containing the image file name , the extracted sample order, and the
    extracted image file number.
    """
    # Generate a list of image file names
    try:
        os.chdir(path=path_ss_img)
        pattern = '*.' + 'png'
        files_list = glob(pattern)

        # Empty tuple list for storing image file names the order the sample was run so that the impage is inserted
        # into the right place in the Excel workbook.
        tuple_list = []

        # Prepare the list of image files for sorting
        for image in files_list:
            image_file_split_array = image.split('_')
            sample_order = int(image_file_split_array[1])
            image_file_num = int(image_file_split_array[5].strip('.png'))
            tuple_list.append((image, sample_order, image_file_num))

        # Sort the tuple of image files.
        tuple_list.sort(key=lambda x: x[2])
        tuple_list.sort(key=lambda x: x[1])
        return tuple_list
    except:
        raise FileNotFoundError('Something is wrong with the Image File folder or Image File names. Please check. \n '
                                'Image file names must be of the format: BRD-0629_4_181029_results_affinity_1.png')


def spr_insert_images(tuple_list, worksheet, path_ss_img, path_senso_img):
    """

    :param tuple_list: List of tuples containing (image_file_name, sample_order, image_file_num)
    :param worksheet: xlsxwriter object used to insert the images to a worksheet
    :param path_ss_img: Directory to the steady state images to insert.
    :param path_senso_img: Directory to the sensorgram images to insert.
    :return: None
    """
    # Format the rows and columns in the worksheet to fit the images.
    num_images = len(tuple_list)

    # Set height of each row
    for row in range(1, num_images + 1):
        worksheet.set_row(row=row, height=235)

    # Set the width of each column
    worksheet.set_column(first_col=3, last_col=4, width=58)

    row = 2
    for image, sample_order, image_file_num in tuple_list:
        worksheet.insert_image('D' + str(row), path_ss_img + '/' + image)
        worksheet.insert_image('E' + str(row), path_senso_img + '/' + image)
        row += 1


def spr_binding_top_for_dot_file(report_pt_file, df_cmpd_set, instrument):
    """This method calculates the binding in RU at the top concentration.

        :param report_pt_file: reference to the report point file exported from the Biacore Instrument.
        :param df_cmpd_set: DataFrame containing the compound set data. This is used to extract the binding
        RU at the top concentration of compound tested.
        :param instrument: The instrument as a string. (e.g. 'BiacoreS200', 'Biacore1, 'Biacore2')
        :returns Series containing the RU at the top concentration tested for each compound in the order tested.
        """
    if (instrument != 'BiacoreS200') & (instrument != 'Biacore1') & (instrument != 'Biacore2'):
        raise ValueError('Instrument argument must be BiacoreS200, Biacore1, or Biacore2')

    try:
        # Read in data
        df_rpt_pts_all = pd.read_excel(report_pt_file, sheet_name='Report Point Table', skiprows=3)
    except:
        raise FileNotFoundError('The files could not be imported please check.')

    # Biacore instrument software for the S200 and T200 instruments exports different column names.
    # Check that the columns in the report point file match the expected values.
    if (instrument=='Biacore1') | (instrument == 'Biacore2'):
        expected_cols = ['Cycle', 'Fc', 'Time', 'Window', 'AbsResp', 'SD', 'Slope', 'LRSD', 'Baseline', 'RelResp',
                         'Report Point', 'AssayStep', 'AssayStepPurpose', 'Buffer', 'CycleType', 'Temp',
                         'Sample_1_Sample', 'Sample_1_Ligand', 'Sample_1_Conc', 'Sample_1_MW', 'General_1_Solution']

    # Check that the columns in the report point file match the expected values.
    if instrument == 'BiacoreS200':
        expected_cols = ['Unnamed: 0', 'Cycle','Fc','Report Point','Time [s]','Window [s]','AbsResp [RU]','SD',
                     'Slope [RU/s]','LRSD','RelResp [RU]',	'Baseline',	'AssayStep','Assay Step Purpose',
                    'Buffer','Cycle Type','Temp','Sample_1_Barcode','Sample_1_Conc [µM]','Sample_1_Ligand',
                         'Sample_1_MW [Da]', 'Sample_1_Sample', 'General_1_Solution']

    if df_rpt_pts_all.columns.tolist() != expected_cols:
        raise ValueError('The columns in the report point file do not match the expected names.')

    # For BiacoreS200
    # Remove first column
    if instrument == 'BiacoreS200':
        df_rpt_pts_trim = df_rpt_pts_all.iloc[:, 1:]

        # Remove other not needed columns
        df_rpt_pts_trim = df_rpt_pts_trim.loc[:,
                      ['Cycle', 'Fc', 'Report Point', 'Time [s]', 'RelResp [RU]', 'AssayStep', 'Cycle Type',
                       'Sample_1_Conc [µM]',
                       'Sample_1_Sample']]

    # For Biacore T200 and T100
    else:
        # Remove other not needed columns
        df_rpt_pts_trim = df_rpt_pts_all.loc[:,
                          ['Cycle', 'Fc', 'Report Point', 'Time', 'RelResp', 'AssayStep', 'CycleType',
                           'Sample_1_Conc',
                           'Sample_1_Sample']]

    # Remove not needed rows.
    df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Report Point'] == 'binding']
    df_rpt_pts_trim = df_rpt_pts_trim[(df_rpt_pts_trim['AssayStep'] != 'Startup') &
                                      (df_rpt_pts_trim['AssayStep'] != 'Solvent correction')]

    # Create a new column of BRD 4 digit numbers to merge
    df_rpt_pts_trim['BRD_MERGE'] = df_rpt_pts_trim['Sample_1_Sample'].str.split('_', expand=True)[0]
    df_cmpd_set['BRD_MERGE'] = 'BRD-' + df_cmpd_set['Broad ID'].str[9:13]

    # Convert compound set concentration column to float so DataFrames can be merged.
    df_cmpd_set['Test [Cpd] uM'] = df_cmpd_set['Test [Cpd] uM'].astype('float')

    # Merge the report point DataFrame and compound set DataFrame which results in a new Dataframe with only the
    # data for the top concentrations run.
    df_rpt_pts_trim = pd.merge(left=df_rpt_pts_trim, right=df_cmpd_set,
                               left_on=['BRD_MERGE', 'Sample_1_Conc [µM]'],
                               right_on=['BRD_MERGE','Test [Cpd] uM'], how='inner')

    # Filter out non-corrected data.
    df_rpt_pts_trim['FC_Type'] = df_rpt_pts_trim['Fc'].str.split(' ', expand=True)[1]
    df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['FC_Type'] == 'corr']

    # If a compound was run more than once, such as a control, we need to drop the duplicate values.
    df_rpt_pts_trim = df_rpt_pts_trim.drop_duplicates(['Fc', 'Sample_1_Sample'])

    # Need to resort the Dataframe
    # Create sorting column
    df_rpt_pts_trim['sample_order'] = df_rpt_pts_trim['Sample_1_Sample'].str.split('_', expand=True)[1]
    df_rpt_pts_trim = df_rpt_pts_trim.sort_values(['Cycle', 'sample_order'])
    df_rpt_pts_trim = df_rpt_pts_trim.reset_index(drop=True)

    return df_rpt_pts_trim['RelResp [RU]']

def spr_create_dot_upload_file(config_file, df_cmpd_set = pd.read_clipboard()):
    import configparser

    try:
        config = configparser.ConfigParser()
        config.read(config_file)

        # Get all of the file paths from the configuration file and store in variables so they are available
        path_ss_img = config.get('paths', 'path_ss_img')
        path_senso_img = config.get('paths', 'path_senso_img')
        path_ss_txt = config.get('paths', 'path_ss_txt')
        path_senso_txt = config.get('paths', 'path_senso_txt')
        path_report_pt = config.get('paths', 'path_report_pt')

        # Get all of the metadata variables
        num_fc_used = config.get('meta','num_fc_used')
        experiment_date = config.get('meta','experiment_date')
        project_code = config.get('meta','project_code')
        operator = config.get('meta','operator')
        instrument = config.get('meta','instrument')
        protocol = config.get('meta','protocol')
        chip_lot = config.get('meta','chip_lot')
        nucleotide = config.get('meta','nucleotide')
        raw_data_filename = config.get('meta','raw_data_filename')
        directory_folder = config.get('meta','directory_folder')
        fc2_protein_BIP = config.get('meta','fc2_protein_BIP')
        fc2_protein_RU = float(config.get('meta','fc2_protein_RU'))
        fc2_protein_MW = float(config.get('meta','fc2_protein_MW'))
        fc3_protein_BIP = config.get('meta','fc3_protein_BIP')
        fc3_protein_RU = float(config.get('meta','fc3_protein_RU'))
        fc3_protein_MW = float(config.get('meta','fc3_protein_MW'))
        fc4_protein_BIP = config.get('meta','fc4_protein_BIP')
        fc4_protein_RU = float(config.get('meta','fc4_protein_RU'))
        fc4_protein_MW = float(config.get('meta','fc4_protein_MW'))
    except:
        raise FileNotFoundError('Something is wrong with the config file. Please check.')

    # Start building the final Dotmatics DataFrame
    df_final_for_dot = pd.DataFrame()

    # Start by adding the Broad ID in the correct order.
    num_fc_used = int(num_fc_used)
    df_final_for_dot['BROAD_ID'] = pd.Series(dup_item_for_dot_df(df_cmpd_set, col_name='Broad ID',
                                                                 times_dup=num_fc_used))

    # Add the Project Code.  Get this from the config file.
    df_final_for_dot['PROJECT_CODE'] = project_code

    #  Add an empty column called curve_valid
    df_final_for_dot['CURVE_VALID'] = ''

    # Add an empty column called steady_state_img
    df_final_for_dot['STEADY_STATE_IMG'] = ''

    # Add an empty column called 1to1_img
    df_final_for_dot['1to1_IMG'] = ''

    # Add the starting compound concentrations
    df_final_for_dot['TOP_COMPOUND_UM'] = pd.Series(dup_item_for_dot_df(df_cmpd_set, col_name='Test [Cpd] uM',
                                                                 times_dup=num_fc_used))

    # Extract the RU Max for each compound using the report point file.
    df_final_for_dot['RU_TOP_CMPD'] = spr_binding_top_for_dot_file(report_pt_file=path_report_pt,
    df_cmpd_set=df_cmpd_set, instrument=instrument)

    # Extract the steady state data and add to DataFrame
    # Read in the steady state text file into a DataFrame
    df_ss_txt = pd.read_csv(path_ss_txt, sep='\t')

    # Create new columns to sort the DataFrame as the original is out of order.
    df_ss_txt['sample_order'] = df_ss_txt['Image File'].str.split('_', expand=True)[1]
    df_ss_txt['sample_order'] = pd.to_numeric(df_ss_txt['sample_order'])
    df_ss_txt['img_file_num'] = df_ss_txt['Image File'].str.split('_', expand=True)[5]
    df_ss_txt = df_ss_txt.sort_values(by=['sample_order', 'img_file_num'])
    df_ss_txt = df_ss_txt.reset_index(drop=True)
    df_ss_txt['KD_SS_UM'] = df_ss_txt['KD (M)'] * 1000000

    # Add the KD steady state
    df_final_for_dot['KD_SS_UM'] = df_ss_txt['KD_SS_UM']

    # Add the chi2_steady_state_affinity
    df_final_for_dot['CHI2_SS_AFFINITY'] = df_ss_txt['Chi² (RU²)']

    # Add the Fitted_Rmax_steady_state_affinity
    df_final_for_dot['FITTED_RMAX_SS_AFFINITY'] = df_ss_txt['Rmax (RU)']

    # Extract the sensorgram data and add to DataFrame
    # Read in the sensorgram data into a DataFrame
    df_senso_txt = pd.read_csv(path_senso_txt, sep='\t')
    df_senso_txt['sample_order'] = df_senso_txt['Image File'].str.split('_', expand=True)[1]
    df_senso_txt['sample_order'] = pd.to_numeric(df_senso_txt['sample_order'])
    df_senso_txt['img_file_num'] = df_senso_txt['Image File'].str.split('_', expand=True)[5]
    df_senso_txt = df_senso_txt.sort_values(by=['sample_order', 'img_file_num'])
    df_senso_txt = df_senso_txt.reset_index(drop=True)

    # Add columns from df_senso_txt
    df_final_for_dot['KA_1_1_BINDING'] = df_senso_txt['ka (1/Ms)']
    df_final_for_dot['KD_LITTLE_1_1_BINDING'] = df_senso_txt['kd (1/s)']
    df_final_for_dot['KD_1_1_BINDING_UM'] = df_senso_txt['KD (M)'] * 1000000
    df_final_for_dot['chi2_1_1_binding'] = df_senso_txt['Chi² (RU²)']

    # Not sure what this is???
    df_final_for_dot['U_VALUE_1_1_BINDING'] = ''
    # Not sure what this is??

    # Continue creating new columns
    df_final_for_dot['FITTED_RMAX_1_1_BINDING'] = df_senso_txt['Rmax (RU)']
    df_final_for_dot['COMMENTS'] = ''

    # Rename the flow channels and add the flow channel column
    df_senso_txt['FC'] = df_senso_txt['Curve'].apply(lambda x: x.replace('c', 'C'))
    df_senso_txt['FC'] = df_senso_txt['FC'].apply(lambda x: x.replace('=', ''))
    df_senso_txt['FC'] = df_senso_txt['FC'].apply(lambda x: x.replace(' ', ''))
    df_final_for_dot['FC'] = df_senso_txt['FC']

    # Add protein RU
    protein_ru_dict = {'FC2-1Corr': fc2_protein_RU, 'FC3-1Corr' : fc3_protein_RU, 'FC4-1Corr' : fc4_protein_RU}
    df_final_for_dot['PROTEIN_RU'] = df_final_for_dot['FC'].map(protein_ru_dict)

    # Add protein MW
    protein_mw_dict = {'FC2-1Corr': fc2_protein_MW, 'FC3-1Corr' : fc3_protein_MW, 'FC4-1Corr' : fc4_protein_MW}
    df_final_for_dot['PROTEIN_MW'] = df_final_for_dot['FC'].map(protein_mw_dict)

    # Add the MW for each compound.
    df_final_for_dot['MW'] = pd.Series(dup_item_for_dot_df(df_cmpd_set, col_name='MW',
                                                           times_dup=num_fc_used))

    # Add protein BIP
    protein_bip_dict = {'FC2-1Corr': fc2_protein_BIP, 'FC3-1Corr' : fc3_protein_BIP, 'FC4-1Corr' : fc4_protein_BIP}
    df_final_for_dot['PROTEIN_ID'] = df_final_for_dot['FC'].map(protein_bip_dict)

    # Continue adding columns to final DataFrame
    df_final_for_dot['INSTRUMENT'] = instrument
    df_final_for_dot['EXP_DATE'] = experiment_date
    df_final_for_dot['NUCLEOTIDE'] = nucleotide
    df_final_for_dot['CHIP_LOT'] = chip_lot
    df_final_for_dot['OPERATOR'] = operator
    df_final_for_dot['PROTOCOL_ID'] = protocol
    df_final_for_dot['RAW_DATA_FILE'] = raw_data_filename
    df_final_for_dot['DIR_FOLDER'] = directory_folder

    # Add the unique ID #
    df_final_for_dot['UNIQUE_ID'] = df_senso_txt['Sample'] + '_' + df_final_for_dot['FC'] + '_' + project_code + \
                                    '_' + experiment_date + '_' + df_senso_txt['img_file_num']

    # Add image file paths
    df_final_for_dot['SS_IMG_ID'] = path_ss_img + '/' + df_ss_txt['Image File']
    df_final_for_dot['SENSO_IMG_ID'] = path_senso_img + '/' + df_senso_txt['Image File']

    # Add the Rmax_theoretical.
    # Note couldn't do this before as I needed to add protein MW and RU first.
    df_final_for_dot['RMAX_THEORETICAL'] = round((df_final_for_dot['MW'] / df_final_for_dot['PROTEIN_MW']) \
                                           * df_final_for_dot['PROTEIN_RU'], 2)

    # Calculate Percent Binding
    df_final_for_dot['%_BINDING_TOP'] = round((df_final_for_dot['RU_TOP_CMPD'] / df_final_for_dot[
        'RMAX_THEORETICAL']) * 100, 2)

    # Rearrange the columns for the final DataFrame (without images)
    df_final_for_dot = df_final_for_dot.loc[:, ['BROAD_ID', 'PROJECT_CODE', 'CURVE_VALID', 'STEADY_STATE_IMG',
       '1to1_IMG', 'TOP_COMPOUND_UM', 'RMAX_THEORETICAL', 'RU_TOP_CMPD', '%_BINDING_TOP', 'KD_SS_UM',
       'CHI2_SS_AFFINITY', 'FITTED_RMAX_SS_AFFINITY', 'KA_1_1_BINDING',
       'KD_LITTLE_1_1_BINDING', 'KD_1_1_BINDING_UM', 'chi2_1_1_binding',
       'U_VALUE_1_1_BINDING', 'FITTED_RMAX_1_1_BINDING', 'COMMENTS', 'FC',
       'PROTEIN_RU', 'PROTEIN_MW', 'PROTEIN_ID', 'MW', 'INSTRUMENT',
       'EXP_DATE', 'NUCLEOTIDE', 'CHIP_LOT', 'OPERATOR', 'PROTOCOL_ID',
       'RAW_DATA_FILE', 'DIR_FOLDER', 'UNIQUE_ID', 'SS_IMG_ID', 'SENSO_IMG_ID']]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('/Users/bfulroth/PycharmProjects/IdeaTesting/181107_test_file_final5.xlsx',
                            engine='xlsxwriter')

    # Convert the DataFrame to an XlsxWriter Excel object.
    df_final_for_dot.to_excel(writer, sheet_name='Sheet1', startcol=0, index=None)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']

    # Add a cell format object to align text center.
    cell_format = workbook.add_format()
    cell_format.set_align('center')
    cell_format.set_align('vcenter')
    worksheet.set_column('A:AI', 25, cell_format)

    # Get list of images files in the steady state and senorgram folders
    # File folder path name
    tuple_list = spr_image_file_list_from_folder(path_ss_img)

    # Insert images into file.
    spr_insert_images(tuple_list, worksheet, path_ss_img, path_senso_img)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

spr_create_dot_upload_file(config_file='/Users/bfulroth/PycharmProjects/IdeaTesting/Test_SPR_Data/Config.txt')

print("Done!")