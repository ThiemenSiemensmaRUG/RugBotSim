import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta as Beta
from scipy.signal import butter, freqz

def calc_conf(val,dec,alpha,beta):
    precision = 1/(10**dec)
    x = np.linspace(val-precision,val+precision,500)
    prob = Beta.pdf(x,alpha,beta)
    # print(val)
    # print(x)
    # print(prob)
    # print(np.dot(x,prob))
    # plt.figure()
    # plt.plot(x,prob)
    # plt.show()
    return np.sum(prob) * (x[10] - x[9]) 
# Initial parameters of the Beta distribution


a = 0
b = 10
np.random.seed(5)

# Number of incoming samples
num_samples = 500
# Calculate the Butterworth filter coefficients
learning_rate =10
bf, af = butter(1,0.99, btype='low', analog=False)
print(bf,af)

mean = 1.777

alpha =2
beta = 2



# Generate some random samples between 0 and 1
samples = np.random.normal(mean,0.1,num_samples)

num_samples = num_samples
# Lists to store results1
unfiltered_means = np.zeros(num_samples)
filtered_means = np.zeros(num_samples)

expected_means = np.zeros(num_samples)
i = 0
conf = []
# Update parameters and calculate means
for sample in samples:
    
    if (sample) < (filtered_means[i-1]):
        beta += ((beta) / (alpha+beta)) * learning_rate 
    else:
        alpha += ((alpha) / (alpha+beta)) * learning_rate

    expected_mean =((alpha-1) / (alpha+beta-2)) *b
    unfiltered_means[i] = expected_mean
    
    ##########################################################################
    expected_means[i] = (expected_mean)
    
    if i>3:
        for j in range(1,len(af)):
            filtered_means[i] += bf[0] *unfiltered_means[i]
            filtered_means[i] -= af[j] * filtered_means[i - j] 
            filtered_means[i] += bf[j] * unfiltered_means[i - j] 
    else:
        filtered_means[i] = np.mean(expected_means[i-(min(1,i)):i])

    #print(np.mean(filtered_means[i-10:i]),filtered_means[i],expected_means[i],sample,(sample) < filtered_means[i],alpha,beta)


    conf.append(calc_conf(((alpha-1) / (alpha+beta-2)) ,1.5 ,alpha,beta   )   )
    i+=1



# Plotting the Beta distribution and updated means over time
x = np.linspace(0, 1, 500)
plt.figure(figsize=(14, 6))

# Plot Beta distribution with current parameters
plt.subplot(131)
plt.plot(np.linspace(a,b,len(x)), Beta.pdf(x, alpha, beta))

plt.title(f'Beta Distribution: alpha={alpha}, beta={beta}')
plt.xlabel('x')
plt.ylabel('Probability Density')


# Plot Beta CDF with current parameters
plt.subplot(132)
plt.plot(conf)
print(f"mode = {np.mean(filtered_means[-10:])}")
print(f"mean = {np.mean(samples)}")
plt.title(f'Beta CDF: alpha={alpha}, beta={beta}')
plt.xlabel('x')
plt.ylabel('Cumulative Probability')




# Plot updated means over time with SMA
plt.subplot(133)
#plt.plot(updated_means, 'b-', label='Updated Mean')
plt.plot(filtered_means, 'g-', label=f'filtered')
#plt.plot(expected_means, 'g--', label=f'unfiltered')
plt.scatter(range(num_samples), samples, c='r', alpha=0.75, s=10,label='Samples')
plt.axhline(y=mean , color='b', linestyle='--', label='Expected Mean')

plt.xlabel('Time (Samples)')
plt.ylabel('Updated Mean')
plt.legend()

plt.tight_layout()
plt.show()
