import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta

def normal_prob(x,sigma,mu):
    return (1/(np.sqrt(2*np.pi*sigma**2))) * np.exp(-((x-mu)**2)/(2*sigma**2)  )

mu_prior = 14.2
sigma_prior = 1




# Initial parameters of the Beta distribution
alpha =0
beta_param = 0

a = 0
b = 1000
np.random.seed(12)

# Initial expected mean (set to 0.5 for demonstration)
expected_mean = b*0.5

# Number of incoming samples
num_samples = 10001


mean = 590.01
# Generate some random samples between 0 and 1
samples = np.random.normal(mean,mean/10,num_samples)

# Lists to store results
updated_means = [500]
count_ = 0
# Update parameters and calculate means
for sample in samples:
    print(sample <updated_means[-1])
    if sample < updated_means[-1]:
        count_+=1
        beta_param += 1
    else:
        alpha += 1
    
    # Calculate new expected mean
    #expected_mean =( alpha )/ (alpha + beta_param)
    if len(updated_means) < 10:
        updated_means.append((( alpha )/ (alpha + beta_param)) *b)
        print(updated_means)
    else:
        temp = np.array(updated_means[:-9].append((( alpha )/ (alpha + beta_param)) *b)).mean()
  
        print(temp)
        updated_means.append(temp)

# Function to compute Simple Moving Average (SMA)
def compute_sma(data, window_size):
    sma = []
    for i in range(len(data)):
        start = max(0, i - window_size + 1)
        sma.append(np.mean(data[start:i+1]))
    return sma

# Compute SMA with window size
sma_window_size = 100
sma_updated_means = compute_sma(updated_means, sma_window_size)
print(count_/num_samples)
# Plotting the Beta distribution and updated means over time
x = np.linspace(0, 1, 500)
plt.figure(figsize=(14, 6))

# Plot Beta distribution with current parameters
plt.subplot(121)
plt.plot(x * b, beta.pdf(x, alpha, beta_param))
plt.title(f'Beta Distribution: alpha={alpha}, beta={beta_param}')
plt.xlabel('x')
plt.ylabel('Probability Density')

# Plot updated means over time with SMA
plt.subplot(122)
#plt.plot(updated_means, 'b-', label='Updated Mean')
plt.plot(sma_updated_means, 'g-', label=f'SMA ({sma_window_size})')
plt.scatter(range(num_samples), samples, c='r', alpha=0.75, s=10,label='Samples')
plt.axhline(y=mean , color='b', linestyle='--', label='Expected Mean')
plt.title(f'Updated Mean over Time (SMA {sma_window_size})')
plt.xlabel('Time (Samples)')
plt.ylabel('Updated Mean')
plt.legend()

plt.tight_layout()
plt.show()
