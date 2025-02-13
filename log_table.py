import numpy as np
from scipy.stats import norm
import pandas as pd



measured_rdcs = {

    22: -4.294,
    23: -2.326,
    24: -13.433,
    25: -10.596,
    26: -5.413,
    28: -16.158,
    30: -8.662,
    31: -13.968,
    32: -16.039,

}

pred_rdcs =  {
    22: -5.9812,
    23: -0.0327,
    24: -15.0125,
    25: -13.721,
    26: -5.4285,
    28: -17.5376,
    30: -6.403,
    31: -13.8255,
    32: -17.9302,
}
rdc_df = pd.DataFrame({
    'Residue': measured_rdcs.keys(),
    'Measured': measured_rdcs.values(),
    'predicted':[pred_rdcs[residue]for residue in measured_rdcs.keys()]
})
def calculate_magnitude(row1, row2):

    measured_1, measured_2 = row1 ['Measured'],row2 ['Measured']
    predicted_1, predicted_2 = row1 ['predicted'], row2 ['predicted']

    return np.sqrt((measured_1-measured_2)**2 + (predicted_1-predicted_2)**2)
residues = rdc_df['Residue']
magnitude_matrix= pd.DataFrame(index= residues, columns=residues)

for i, row1 in rdc_df.iterrows():
    for j, row2 in rdc_df.iterrows():
        magnitude_matrix.loc[row1['Residue'],row2['Residue']] = calculate_magnitude(row1, row2)




calculate_magnitude(row1,row2 )
magnitude_matrix=magnitude_matrix.astype(float)
print('magnitude matrix:')
print(magnitude_matrix)
