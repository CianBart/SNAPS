import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

x_values = np.linspace(-10, 10, 500)
mu = 0        # Mean at the center
sigma_values = [1,2,3] # Standard deviation


plt.figure(figsize=(8, 6))
for sigma in sigma_values:
    log_prob_values = [norm.logpdf(x,mu,sigma ) for x in x_values]
    plt.plot(x_values, log_prob_values,label=rf"$\sigma={sigma}$")
plt.title("Log-Probability of Gaussian Distribution")
plt.xlabel("x")
plt.ylabel("Log Probability")
plt.grid(True)
plt.legend()
plt.show()



