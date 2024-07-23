
import numpy as np
# nu = 1250, p = 0.953655, var = 0.00188136, O = 0, delta = 0.0195939
# probability = 0.000908081
eta = 1250
var = 0.00188136
p =  0.953655
sample = 0

delta = np.exp(-1* (eta * var)) * (0.5 -p )*(0.5 -p )
print(delta)
prob = delta * (1-p) + (1-delta) * sample


print(prob)
#robability = 5.90853e-05