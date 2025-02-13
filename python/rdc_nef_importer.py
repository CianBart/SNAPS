from pynmrstar import Entry

from lib.nef_lib import loop_row_dict_iter, loop_row_namespace_iter, loop_to_dataframe


def main(file_name):
    entry =  Entry.from_file(file_name)
    print('entry id',entry.entry_id)
    spectra = entry.get_saveframes_by_category('nef_nmr_spectrum')

    hsqc_1 = [spectrum for spectrum in spectra if spectrum.name == 'nef_nmr_spectrum_hsqc`1`'][0]
    peaks = hsqc_1.get_loop_by_category('nef_peak')

    print('as variables')
    for row in loop_row_namespace_iter(peaks):
        print(row.index, row.chain_code_1, row.sequence_code_1, row.residue_name_1, row.atom_name_1, row.height, row
.height_uncertainty)

    print('as dictionaries')
    for row in loop_row_dict_iter(peaks):
        print(row)

    print('as pandas dataframe')
    dataframe =  loop_to_dataframe(peaks)
    print(dataframe)



if __name__ == '__main__':
    main('../test_data/Sec5Part4.nef')
