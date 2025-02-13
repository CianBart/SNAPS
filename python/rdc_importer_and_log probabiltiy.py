import sys

import pandas as pd

from lib.rdcs_lib import saveframe_to_dataframes, get_nef_entry, \
    magnitude_matrix_to_log_probability_matrix, \
    pred_measured_to_magnitude_matrix, index_names_to_snaps, \
    add_penalty_tables, check_for_single_residue_and_chain, build_log_probability_from_entry, \
    build_magnitude_log_probability_tables, combine_penalty_tables

from pynmrstar import  Entry
from pandas import DataFrame





if __name__ == '__main__':
    entry = get_nef_entry('../test_data/data_gb3_rdcs.nef')
    dataframe_predicted, dataframe_measured=build_log_probability_from_entry(entry, predicted='NH_pred', measured='NH_measured')
    RDC_log_probability_data=build_magnitude_log_probability_tables(dataframe_measured,dataframe_predicted)
    combine_penalty_tables(RDC_log_probability_data, RDC_log_probability_data)






