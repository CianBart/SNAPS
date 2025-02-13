import numpy as np
from scipy.stats import norm
import pandas as pd

import log_prob
from log_table import magnitude_matrix

sigma= 2.97

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
measured_df = pd.DataFrame({
    'Residue': measured_rdcs.keys(),
    'Measured': measured_rdcs.values(),

})
predicted_df=pd.DataFrame({
    'Residue': pred_rdcs.keys(),
    'Predicted': pred_rdcs.values(),
 })

residues_measured=measured_df['Residue']
residues_predicted= predicted_df['Residue']
magnitude_matrix=pd.DataFrame(index=residues_measured,columns=residues_predicted)

for i, row_measured in measured_df.iterrows():
    for j, row_predicted in predicted_df.iterrows():
        magnitude_matrix.loc[row_measured['Residue'],row_predicted['Residue']]=np.sqrt((row_measured['Measured']-row_predicted['Predicted'])**2)
        log_probability_matrix = magnitude_matrix.map(lambda x: norm.logpdf(x, loc=0, scale=sigma))


magnitude_matrix=magnitude_matrix.astype(float)

def output():
    pass
   # print('magnitude matrix:')
   # print(magnitude_matrix)
   # print('\nLog probability matrix')
    #print(log_probability_matrix)

#output()