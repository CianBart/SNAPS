import sys

import pandas as pd

from python.lib.nef_lib import loop_row_dict_iter, loop_row_namespace_iter, loop_to_dataframe
from pynmrstar import  Entry, Saveframe

from python.lib.rdcs_lib import frame_to_rdcs, pred_measured_to_magnitude


def main(file_name):

    entry =  Entry.from_file(file_name)
    #print('entry id',entry.entry_id)
    frames = entry.get_saveframes_by_category('nef_rdc_restraint_list')

    pred_frame_name = 'NH_pred'

    rdc_frame = [frame for frame in frames if frame.name == f'nef_rdc_restraint_list_{pred_frame_name}'][0]

    dataframe_predicted = frame_to_rdcs(rdc_frame)

    measured_frame_name = 'NH_measured'

    rdc_frame = [frame for frame in frames if frame.name == f'nef_rdc_restraint_list_{measured_frame_name}'][0]

    dataframe_measured = frame_to_rdcs(rdc_frame)

    print(dataframe_measured)

    log_probability = pred_measured_to_magnitude(dataframe_predicted, dataframe_measured)
    print(log_probability)

    # rdcm = [meas for meas in frames if meas.name == 'nef_rdc_restraint_list_NH_measured']
    # measured = rdcm[0]
    # measured_rdc= measured.get_loop_by_category('nef_rdc_restraint')
    #
    # for row in loop_row_namespace_iter(measured_rdc):
    #     print(row.index, row.restraint_id, row.restraint_combination_id, row.chain_code_1, row.sequence_code_1,
    #           row.residue_name_1, row.atom_name_1, row.chain_code_2, row.sequence_code_2, row.sequence_code_2,
    #           row.residue_name_2, row.atom_name_2, row.weight, row.target_value, row.target_value_uncertainty)
    #
    #
    # print('measured steric RDCs as dictionaries')
    # for row in loop_row_dict_iter(measured_rdc):
    #     print(row)
    #
    # print('measured steric RDCs as pandas dataframe')
    # dataframe_measured = loop_to_dataframe(measured_rdc)
    # print(dataframe_measured)

    # magnitude_matrix=




if __name__ == '__main__':
    main('../test_data/data_gb3_rdcs.nef')







