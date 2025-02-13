
from pandas.testing import assert_frame_equal
import sys

import pandas as pd

from magnitude_table import residues_measured, residues_predicted
from python.lib.nef_lib import loop_row_dict_iter, loop_row_namespace_iter, loop_to_dataframe
from pynmrstar import  Entry, Saveframe

from lib.rdcs_lib import  pred_measured_to_magnitude_matrix,magnitude_matrix_to_log_probability_matrix  # frame_to_rdcs,


def test_magnitude_matrix():
    # create 2 tables
    # calc pdf using library function
    # use assert almost equals

    predicted_data = [
        [0,'ALA', -5.9812],
        [1,'GLY', -0.0327],
        [2,'SER', -15.0215]
    ]
    residues_predicted = pd.DataFrame(predicted_data, columns=['sequence_code','residue_name', 'target_value'])

    measured_data= [
        [0,'ALA', -4.294],
        [1,'GLY', -2.326],
        [2,'SER', -13.433]
    ]

    residues_measured = pd.DataFrame(measured_data, columns=['sequence_code','residue_name', 'target_value'])

    residues_predicted['sequence_code']= residues_predicted['sequence_code'].astype(str)
    residues_measured['sequence_code'] = residues_measured['sequence_code'].astype(str)

    magnitude_matrix=pred_measured_to_magnitude_matrix(residues_measured,residues_predicted)


    log_probability = magnitude_matrix_to_log_probability_matrix(magnitude_matrix)

    correct_log_probabilities= [
        [-2.342260,-9.998277,-58.458567],
        [-7.599182,-3.548551,-81.506799],
        [-28.683600,-90.702959,-2.180605]
    ]
    correct_log_probabilities_df= pd.DataFrame(correct_log_probabilities, index=log_probability.index, columns= log_probability.columns).transpose()
    correct_log_probabilities_df.index.name  = 'sequence_code'
    correct_log_probabilities_df.columns.name = 'sequence_code'

    assert_frame_equal(left=log_probability, right= correct_log_probabilities_df, check_exact= False) #, atol=1e-5)





