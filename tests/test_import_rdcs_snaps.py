import sys

import pytest
from pathlib import Path
import pandas as pd


from pandas.testing import assert_frame_equal


from SNAPS_assigner import SNAPS_assigner
from SNAPS_importer import SNAPS_importer, SnapsImportException


TEST_DATA = Path(__file__).parent.parent / 'test_data'

def test_import_aa_type_info_file():
    importer = SNAPS_importer()
    importer.import_obs_shifts(TEST_DATA / 'unittest_data_gb3_rdcs.nef', 'nef')
    result = importer.import_aa_type_info_file(TEST_DATA / 'test_rdc_aa_info.txt')
    data = {
        'Atom_type': ['22Asp', '23Ala', '24Glu', '25Thr'],
        'SS_name': ['22Asp', '23Ala', '24Glu', '25Thr'],
        'C': [174.798, 179.383, 179.303, 177.049],
        'CA': [52.514 ,54.559,66.844, 66.844  ],
        'CB': [42.38, 17.61 ,29.05 ,67.89 ],
        'H': [7.373,8.393, 8.487, 8.409],
        'HA': [4.754,3.374 ,3.886,3.705],
        'N': [115.403,121.205,119.144,117.485],
        'SS_class': ['ACDEFGHIKLMNPQRSTVWY', 'AVI', 'AVI', 'ACDEFGHIKLMNPQRSTVWY'],
        'SS_class_m1': ['ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY']
    }
    expected = pd.DataFrame(data, index=data['SS_name'], columns=['SS_name', 'C', 'CA', 'CB', 'H', 'HA', 'N',
                                                                  'SS_class', 'SS_class_m1'])
    expected.columns.names = ['Atom_type']
    assert_frame_equal(expected, result, check_exact=False, rtol=0.01)


def test_import_aa_type_info_out():
    importer = SNAPS_importer()
    importer.import_obs_shifts(TEST_DATA / 'unittest_data_gb3_rdcs.nef', 'nef')
    result_out = importer.import_aa_type_info_file(TEST_DATA / 'test_rdc_aa_info_out.txt')
    data_out = {
        'Atom_type': ['22Asp', '23Ala', '24Glu', '25Thr'],
        'SS_name': ['22Asp', '23Ala', '24Glu', '25Thr'],
        'C': [174.798, 179.383, 179.303, 177.049],
        'CA': [52.514, 54.559, 66.844, 66.844],
        'CB': [42.38, 17.61, 29.05, 67.89],
        'H': [7.373, 8.393, 8.487, 8.409],
        'HA': [4.754, 3.374, 3.886, 3.705],
        'N': [115.403, 121.205, 119.144, 117.485],
        'SS_class': ['ACDEFGHIKLMNPQRSTVWY', 'CDEFGHKLMNPQRSTWY', 'CDEFGHKLMNPQRSTWY', 'ACDEFGHIKLMNPQRSTVWY'],
        'SS_class_m1': ['ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY']
    }

    expected_out = pd.DataFrame(data_out, index=data_out['SS_name'], columns=['SS_name', 'C', 'CA', 'CB', 'H', 'HA',
                                                                              'N', 'SS_class', 'SS_class_m1'])
    expected_out.columns.names = ['Atom_type']
    assert_frame_equal(expected_out, result_out, check_exact=False, rtol=0.01)


def test_import_rdc_data():
    importer = SNAPS_importer()
    imported_magnitude= importer.import_rdc_data('../test_data/unittest_data_gb3_rdcs.nef')
    SS_name = ['22D', '23A', '24E', '25T' ]
    Res_name=['22Asp', '23Ala', '24Glu', '25Thr']

    correct_magnitude_matrix= [

        [1.6872,-4.2613,10.7275,9.427],
        [3.6552,-2.2933,12.6955,11.395],
        [-7.4518,-13.4003,1.5885,0.288],
        [-4.6148,-10.5633,4.4255,3.125]


    ]

    correct_magnitude_matrix_df = pd.DataFrame(correct_magnitude_matrix, index= Res_name, columns=SS_name )


    correct_magnitude_matrix_df.index.name = 'Res_name'
    correct_magnitude_matrix_df.columns.name = 'SS_name'
    print(correct_magnitude_matrix_df)
    assert_frame_equal(left=imported_magnitude,right=correct_magnitude_matrix_df,check_index_type= True,check_column_type=True, check_exact=False)




@pytest.mark.skip('unknown errors')
def test_SNAPS_log_probability():

    assigner = SNAPS_assigner()

    pars=  pd.read_csv(TEST_DATA / 'self_pars.txt')


    assigner.obs = pd.read_csv(TEST_DATA / 'test_rdc_obs.txt', sep='\s+')




    assigner.preds = pd.read_csv(TEST_DATA / 'test_rdc_preds.txt', sep='\s+')
    #assigner.pars = pars
    imported_log_probability= assigner.calc_log_prob_matrix()
    print('assigned\n ',imported_log_probability, '======================================================')

    SS_name = ['22D', '23A', '24E', '25T']
    Res_name = ['22Asp', '23Ala', '24Glu', '25Thr']

    correct_log_probability = [

        [  -3.957731,  -311.117293, -219.507903,  -436.397199 ],
        [-310.133819,    -3.957731, -168.817722, -1285.522564 ],
        [-219.215628,  -169.508921,   -3.957731,  -737.300977 ],
        [-436.849223, -1286.958062, -738.045276,    -3.957731 ]
        ]

    correct_log_probability_df = pd.DataFrame(correct_log_probability, columns=SS_name )
    correct_log_probability_df.index.name = 'Res_name'
    correct_log_probability_df.columns.name = 'SS_name'
    assert_frame_equal(left=imported_log_probability,right=correct_log_probability_df,check_index_type= True,check_column_type=True, check_exact=False)









def test_rdc_log_probability():
    importer = SNAPS_importer()
    assigner = SNAPS_assigner()
    imported_magnitude = importer.import_rdc_data('../test_data/unittest_data_gb3_rdcs.nef')
    imported_log_probability= assigner.calc_rdc_log_prob_matrix(imported_magnitude)
    SS_name = ['22D', '23A', '24E', '25T']
    Res_name = ['22Asp', '23Ala', '24Glu', '25Thr']

    correct_log_probability = [

        [-2.342260, - 9.998277, - 58.458567, - 45.353103],
        [- 7.599182, - 3.548551, - 81.506799 ,- 65.841951],
        [- 28.683600, - 90.702959, - 2.180605, - 0.960411],
        [- 11.567128, - 56.710592, - 10.711464, - 5.801751]
    ]

    correct_log_probability_df = pd.DataFrame(correct_log_probability, index= Res_name, columns=SS_name )
    correct_log_probability_df.index.name = 'Res_name'
    correct_log_probability_df.columns.name = 'SS_name'
    print(correct_log_probability_df)
    assert_frame_equal(left=imported_log_probability,right=correct_log_probability_df,check_index_type= True,check_column_type=True, check_exact=False)

def test_combining_penalty_tables():
    assigner=SNAPS_assigner()

    SS_name = ['22D', '23A', '24E', '25T']
    Res_name = ['22Asp', '23Ala', '24Glu', '25Thr']
    # should probably import these values rather than creating a dataframe for them inside the test function
    rdc_log = pd.read_csv(TEST_DATA / 'rdc_log_probability_matrix.txt', sep='\s+')
    rdc_log=pd.DataFrame(rdc_log, index = Res_name, columns= SS_name)
    rdc_log.index.name = 'Res_name'
    rdc_log.columns.name = 'SS_name'

    # correct_rdc_log_probability = [
    #
    #         [-2.342260, - 9.998277, - 58.458567, - 45.353103],
    #         [- 7.599182, - 3.548551, - 81.506799 ,- 65.841951],
    #         [- 28.683600, - 90.702959, - 2.180605, - 0.960411],
    #         [- 11.567128, - 56.710592, - 10.711464, - 5.801751]
    #     ]
    # correct_RDC_log_probability_df = pd.DataFrame(correct_rdc_log_probability, index= Res_name, columns=SS_name )
    # correct_RDC_log_probability_df.index.name = 'Res_name'
    # correct_RDC_log_probability_df.columns.name = 'SS_name'
# should probably import these values rather than creating a dataframe for them inside the test function

    SNAPS_log= pd.read_csv(TEST_DATA / 'test_rdc_log.txt', sep='\s+')
    SNAPS_log = pd.DataFrame(SNAPS_log, index = Res_name, columns=SS_name)
    SNAPS_log.index.name= 'Res_name'
    SNAPS_log.columns.name = 'SS_name'

    # correct_SNAPS_log_probability = [
    #
    #     [  -3.957731,  -311.117293, -219.507903,  -436.397199 ],
    #     [-310.133819,    -3.957731, -168.817722, -1285.522564 ],
    #     [-219.215628,  -169.508921,   -3.957731,  -737.300977 ],
    #     [-436.849223, -1286.958062, -738.045276,    -3.957731 ]
    #     ]
    #
    # correct_SNAPS_log_probability_df = pd.DataFrame(correct_SNAPS_log_probability, index= Res_name, columns=SS_name )
    # correct_SNAPS_log_probability_df.index.name = 'Res_name'
    # correct_SNAPS_log_probability_df.columns.name = 'SS_name'

    correct_combined_penalty_table= [

        [-6.299991, -321.115570, -277.966470, -481.750302],
        [-317.733001, -7.506282, -250.324521, -1351.364515],
        [-247.899228, -260.211880, -6.138336, -738.261387],
        [-448.416351, -1343.668654, -748.756740, -9.759482]


    ]
    correct_combined_penalty_table_df = pd.DataFrame(correct_combined_penalty_table, index= Res_name, columns=SS_name )
    correct_combined_penalty_table_df.index.name = 'Res_name'
    correct_combined_penalty_table_df.columns.name = 'SS_name'
    combined_tables=assigner.combine_penalty_tables(SNAPS_log,rdc_log)
    assert_frame_equal(left=combined_tables,right=correct_combined_penalty_table_df,check_index_type= True,check_column_type=True, check_exact=False)
@pytest.mark.skip('unknown errors')
def test_matrix_data():
    assigner=SNAPS_assigner()

    obs = pd.read_csv(TEST_DATA / 'test_rdc_obs.txt', sep='\s+')
    preds = pd.read_csv(TEST_DATA / 'test_rdc_preds.txt', sep='\s+')

    SS_name = ['22D', '23A', '24E', '25T']
    Res_name = ['22Asp', '23Ala', '24Glu', '25Thr']
    logs= [
        [-3.957731 ,-311.117293 ,-219.507903 ,-436.397199],
        [-310.133819 ,-3.957731 ,-168.817722 ,-1285.522564],
        [-219.215628 ,-169.508921 ,-3.957731, -737.300977],
        [-436.849223, -1286.958062, -738.045276, -3.957731]
    ]

    log=pd.DataFrame(logs, index=Res_name, columns=SS_name)
    log.index.name='Res_name'
    log.columns.name='SS_name'



    # obs= obs.astype(float)
    # log = log.astype(float)
    # preds = preds.astype(float)
    print('\n obs\n', obs)
    print('preds', preds)
    print('log',log)


    original_log_prob_matrix = log.copy(deep=True)
    print('original\n',original_log_prob_matrix)
    updated_log_prob_matrix = assigner._apply_ss_class_penalties(log, obs, preds)
    print('updated_log_prob_matrix\n',updated_log_prob_matrix)
    diffs = updated_log_prob_matrix - original_log_prob_matrix
    print("Differences in matrix\n", diffs)

    # if diffs != 0:
    #     with pytest.raises(SnapsImportException) as e:
    #
    #          assert "differences in the matrix should be 0"

    EXPECTED_IN_DATA = {
            'Atom_type': ['22Asp', '23Ala', '24Glu', '25Thr'],
            'SS_name': ['22Asp', '23Ala', '24Glu', '25Thr'],
            'C': [174.798, 179.383, 179.303, 177.049],
            'CA': [52.514 ,54.559,66.844, 66.844  ],
            'CB': [42.38, 17.61 ,29.05 ,67.89 ],
            'H': [7.373,8.393, 8.487, 8.409],
            'HA': [4.754,3.374 ,3.886,3.705],
            'N': [115.403,121.205,119.144,117.485],
            'SS_class': ['ACDEFGHIKLMNPQRSTVWY', 'AVI', 'AVI', 'ACDEFGHIKLMNPQRSTVWY'],
            'SS_class_m1': ['ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY', 'ACDEFGHIKLMNPQRSTVWY']
        }
    EXPECTED_COLUMNS = ['SS_name', 'C', 'CA', 'CB', 'H', 'HA', 'N', 'SS_class', 'SS_class_m1']
    EXPECTED_IN = pd.DataFrame(EXPECTED_IN_DATA, index=EXPECTED_IN_DATA['SS_name'], columns=EXPECTED_COLUMNS)
    EXPECTED_IN.columns.names = ['Atom_type']













def test_headings_aa_info():
    importer = SNAPS_importer()
    importer.import_obs_shifts(TEST_DATA / 'unittest_data_gb3_rdcs.nef', 'nef')

    with pytest.raises(SnapsImportException) as e:
        importer.import_aa_type_info_file(TEST_DATA / 'test_rdc_aa_info_bad_header.txt')

    assert 'Unexpected column name(s) [AAA]' in str(e.value)
    assert 'expected column names are:' in str(e.value)
    for name in 'Type SS_name AA'.split():
        assert name in str(e.value)


def test_headings_aa_info_type_column_bad():
    importer = SNAPS_importer()
    importer.import_obs_shifts(TEST_DATA / 'unittest_data_gb3_rdcs.nef', 'nef')

    with pytest.raises(SnapsImportException) as e:
        importer.import_aa_type_info_file(TEST_DATA / 'test_rdc_aa_info_bad_type_column.txt')
    assert "Type column row error: 'Type' column rows can only contain 'in' or 'ex'" in str(e.value)