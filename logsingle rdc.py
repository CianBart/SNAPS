import numpy as np
from scipy.stats import norm

measured_rdc= -4.204
predicted_rdc= -5.9812
sigma = 1

log_prob = norm.logpdf(measured_rdc, loc= predicted_rdc, scale= sigma)

print('log probability for one pair:', log_prob)

magnitude= np.sqrt(predicted_rdc**2 + measured_rdc**2)
print('magnitude for one pair is:',magnitude)



def calculate_logs(row1,row2):

    measured_1, measured_2 = row1 ['Measured'],row2 ['Measured']
    predicted_1, predicted_2 = row1 ['predicted'], row2 ['predicted']

    return  norm.logpdf(row1,loc=row2, scale= sigma)
residues = rdc_df['Residue']
log_matrix= pd.DataFrame(index= residues, columns=residues)

for a, row1 in rdc_df.iterrows():
    for e, row2 in rdc_df.iterrows():
        log_matrix.loc[row1['Residue'],row2['Residue']] = calculate_logs(row1,row2)