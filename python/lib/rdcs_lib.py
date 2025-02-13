import sys



from lib.nef_lib import loop_to_dataframe #loop_row_namespace_iter, #loop_row_dict_iter,

SIGMA= 1
from pandas import DataFrame , merge
from scipy.stats import norm
from pynmrstar import Saveframe, Entry

import math

def get_nef_entry(file_name):
    """
    imports a rdc_nef file from file name
    Args:
        file_name:

    Returns:
        RDC nef_file

    """
    entry = Entry.from_file(file_name)
    return entry

def index_names_to_snaps(dataframe_predicted: DataFrame, dataframe_measured : DataFrame):

    tidy_dataframe_predicted = remove_unnecessary_columns(dataframe_predicted)
    tidy_dataframe_predicted = apply_translation_3_1_protein(tidy_dataframe_predicted)

    tidy_dataframe_measured = remove_unnecessary_columns(dataframe_measured)
    translation_3_lowercase(tidy_dataframe_measured,'residue_name')

    return tidy_dataframe_predicted, tidy_dataframe_measured


def predicted_to_input(entry: Entry, predicted :str):
   # strip out unused columns  (maybe a separate function)
   # check that each rdc is from a single residue and chain (maybe a separate function)
   # build correct naming convention
   # massage column headers
   dataframe_predicted = saveframe_to_dataframes(entry,predicted)
   check_for_single_residue_and_chain(dataframe_predicted)
   return dataframe_predicted

def measured_to_input(entry:Entry, measured:str):

    dataframe_measured= saveframe_to_dataframes(entry, measured)
    check_for_single_residue_and_chain(dataframe_measured)
    return dataframe_measured

def build_log_probability_from_entry(entry:Entry, predicted:str, measured:str):

    dataframe_predicted= predicted_to_input(entry, predicted)
    dataframe_measured= measured_to_input (entry, measured)

    tidy_dataframe_predicted,tidy_dataframe_measured= index_names_to_snaps(dataframe_predicted, dataframe_measured)

    return tidy_dataframe_predicted,tidy_dataframe_measured


def build_magnitude_log_probability_tables(tidy_dataframe_measured:DataFrame, tidy_dataframe_predicted:DataFrame):
    magnitude_matrix = pred_measured_to_magnitude_matrix(tidy_dataframe_predicted, tidy_dataframe_measured)
    #print('magnitude_matrix \n', magnitude_matrix)
    log_prob = magnitude_matrix_to_log_probability_matrix(magnitude_matrix)
    print('log_prob \n', log_prob.to_string())
    return log_prob


def combine_penalty_tables(rdc: DataFrame, snaps: DataFrame ) :
    table = (add_penalty_tables(rdc, snaps))
    print('new table\n', table)


def entry_to_rdc_dataframe(entry: Entry, frame_name:str) -> DataFrame:
    """

    Args:
        entry: RDC nef_file
        frame_name: NH_pred , NH_measured

    Returns: log_probability

    """
    dataframe_predicted=saveframe_to_dataframes(entry, frame_name)
    dataframe_measured=saveframe_to_dataframes(entry,frame_name)

    magnitude_matrix=pred_measured_to_magnitude_matrix(dataframe_predicted,dataframe_measured)
    return magnitude_matrix

def saveframe_to_dataframes(entry:Entry, frame_name:str):
    frames = entry.get_saveframes_by_category('nef_rdc_restraint_list')
    rdc_frame = [frame for frame in frames if frame.name == f'nef_rdc_restraint_list_{frame_name}'][0]
    dataframe = frame_to_rdcs(rdc_frame)

    return dataframe

def frame_to_rdcs(rdc_frame) -> DataFrame:

    rdc = rdc_frame.get_loop('nef_rdc_restraint')
    loop_dataframe = loop_to_dataframe(rdc)

    #for row in loop_row_namespace_iter(rdc):
        #print(row.index, row.restraint_id, row.restraint_combination_id, row.chain_code_1, row.sequence_code_1,
              #row.residue_name_1, row.atom_name_1, row.chain_code_2, row.sequence_code_2, row.sequence_code_2,
              #row.residue_name_2, row.atom_name_2, row.weight, row.target_value, row.target_value_uncertainty)
    #print('steric RDCs as dictionaries')
    #for row in loop_row_dict_iter(rdc):
        #print(row)
    #print('==================================================================================================================================================================================================================================================================================================')
    return loop_dataframe

def pred_measured_to_magnitude_matrix(predicted_df: DataFrame, measured_df: DataFrame) ->  DataFrame:
    """"
        create a magnitude matrix from measured and predicted rdcs

        :param predicted_df: predicted rdcs
        :param measured_df: measured rdcs

        :return:  magnitude matrix

    """
    predicted_df['SS_name'] = predicted_df['sequence_code'].astype(str) + predicted_df['residue_name']
    measured_df['Res_name'] = measured_df['sequence_code'].astype(str) + measured_df['residue_name']


    magnitude_matrix = DataFrame(index=measured_df['Res_name'], columns=predicted_df['SS_name'])


    for i, row_measured in measured_df.iterrows():
        for j, row_predicted in predicted_df.iterrows():
            magnitude_matrix.loc[row_measured['Res_name'],row_predicted['SS_name']] = (
                        float(row_measured['target_value']) - float(row_predicted['target_value']))


    print ('magnitude matrix \n', magnitude_matrix.to_string())
    return magnitude_matrix.astype(float)

def magnitude_matrix_to_log_probability_matrix(magnitude_matrix: DataFrame):

    log_probability_matrix = magnitude_matrix.map(lambda x: norm.logpdf(x, loc=0, scale=SIGMA))
    return log_probability_matrix

def remove_unnecessary_columns(dataframe: DataFrame) ->  DataFrame:

    tidy_table_column_names=['chain_code_1','sequence_code_1','residue_name_1','atom_name_1','weight','target_value']
    dataframe = dataframe[tidy_table_column_names]
    dataframe = dataframe.rename(columns={'chain_code_1':'chain_code','sequence_code_1':'sequence_code','residue_name_1':'residue_name','atom_name_1':'atom_name'})
    return dataframe

def check_for_single_residue_and_chain(df : DataFrame):
    #check that each rdc is from a single residue and chain
    assert df['chain_code_1'].equals(df['chain_code_2']), f" RDC value is from different chains"
    assert df['residue_name_1'].equals(df['residue_name_2']), f"RDC value contains different residues"

def check_dataframe_compatability(rdc : DataFrame , snaps : DataFrame):

    assert rdc.columns.equals(snaps.columns) , f"column's do not match"
    assert rdc.index.equals(snaps.index), f" index's does mot match"

def add_penalty_tables(rdc:DataFrame , snaps : DataFrame):
    """

    Args:
        rdc: penalty table from RDC code
        snaps: penalty table from SNAPS code

    Returns: dataframe with penalty table data of RDC and SNAPS penalties added

    """
    #check_dataframe_compatability(rdc,snaps)

    #snaps=snaps.rename(columns=lambda x: x.lstrip())

    df=snaps + rdc
    # print(snaps.columns)
    #
    # print(snaps.index)
    # print()
    # print(rdc.columns)
    # print(rdc.index)
    # print()
    # print(df.columns)
    # print(df.index)
    # print(df.to_string())
    #sys.exit()

    return df

def log_gaussian_probability(x, mu, sigma):

    log_prob = -((x - mu)**2) / (2 * sigma**2) - math.log(math.sqrt(2 * math.pi * sigma**2))
    return log_prob

def translations_3_1_protein():

    TRANSLATIONS_3_1_PROTEIN = {
        "ALA": "A",
        "ARG": "R",
        "ASN": "N",
        "ASP": "D",
        "CYS": "C",
        "GLU": "E",
        "GLN": "Q",
        "GLY": "G",
        "HIS": "H",
        "ILE": "I",
        "LEU": "L",
        "LYS": "K",
        "MET": "M",
        "PHE": "F",
        "PRO": "P",
        "SER": "S",
        "THR": "T",
        "TRP": "W",
        "TYR": "Y",
        "VAL": "V",
    }
    TRANSLATIONS_1_3_PROTEIN = {
        value: key for (key, value) in TRANSLATIONS_3_1_PROTEIN.items()
    }
    return {"TRANSLATIONS_3_1_PROTEIN": TRANSLATIONS_3_1_PROTEIN, "TRANSLATIONS_1_3_PROTEIN": TRANSLATIONS_1_3_PROTEIN}

def apply_translation_3_1_protein(predicted_df: DataFrame) -> DataFrame:

    """Translate three-letter amino acid codes to one-letter codes in the DataFrame.

     Args:

        predicted_df: DataFrame containing predicted RDCs with three-letter amino acid codes.



    Returns:

        DataFrame with 'residue_name_1' translated to one-letter codes.

    """
    # Get the translation dictionary
    translation_dict = translations_3_1_protein()["TRANSLATIONS_3_1_PROTEIN"]
     # Apply the translation to 'residue_name_1'
    predicted_df['residue_name'] = predicted_df['residue_name'].map(translation_dict)
    return predicted_df

def translation_3_lowercase(df: DataFrame, column_name: str) -> DataFrame:

    df[column_name]=df[column_name].str.capitalize()
    return df


