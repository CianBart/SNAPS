from scipy.stats import norm, multivariate_normal
import scipy.stats as stats
import numpy as np
import pandas as pd



sigma = 1
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
log_prob_total=0.0

def calc_log_prob_rdc(measured_rdcs, pred_rdcs):

    for residue,measured_rdc in measured_rdcs.items():
        if residue not in pred_rdcs:
            print(f'residue {residue} not found in predicted RDCs.')
            continue

        predicted_rdc = pred_rdcs[residue]


        if not isinstance( predicted_rdc, (int,float)):
            print(f'presicted RDC for residue {residue} is not a number: {predicted_rdc}')
            continue



        log_prob = norm.logpdf(measured_rdc,loc=predicted_rdc, scale= sigma)
        magnitude = np.sqrt(predicted_rdc** 2 + measured_rdc** 2)
        #print(f"Residue {residue}: Log Probability = {log_prob}, Magnitude = {magnitude}")




calc_log_prob_rdc(measured_rdcs, pred_rdcs)


#df = pd.DataFrame([measured_rdcs, pred_rdcs])
#print (df)


