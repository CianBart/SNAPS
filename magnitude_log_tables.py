import numpy as np
from scipy.stats import norm
from pandas import DataFrame





measured_rdcs = {

    #('A', '@22', 'H', 'A', '@22', 'N') : (-4.294, 1.0),
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
    #22: -5.9812,
    23: -0.0327,
    24: -15.0125,
    25: -13.721,
    26: -5.4285,
    28: -17.5376,
    30: -6.403,
    31: -13.8255,
    32: -17.9302,
}
measured_df = DataFrame({
    'Residue': measured_rdcs.keys(),
    'Measured': measured_rdcs.values(),

})
predicted_df=DataFrame({
    'Residue': pred_rdcs.keys(),
    'Predicted': pred_rdcs.values(),
 })







def output():
    pass
   # print('magnitude matrix:')
    #print(magnitude_matrix)
    #print('\nLog probability matrix')
    #print(log_probability_matrix)

#output()