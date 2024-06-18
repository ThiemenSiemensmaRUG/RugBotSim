import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import BayesianGaussianMixture

# Generate synthetic 1D data
np.random.seed(42)
n_samples = 1000
X = np.concatenate([np.random.normal(0, 1, int(0.3 * n_samples)),
                    np.random.normal(5, 1, int(0.7 * n_samples))]).reshape(-1, 1)

# Fit Bayesian Gaussian Mixture Model
bgmm = BayesianGaussianMixture(n_components=3, covariance_type='full', max_iter=1000, random_state=42)
bgmm.fit(X)

# Predict cluster labels
labels = bgmm.predict(X)

# Plot clusters
plt.figure(figsize=(10, 6))
plt.hist(X, bins=30, density=True, alpha=0.5, color='b')

x = np.linspace(-3, 8, 1000).reshape(-1, 1)
for i in range(bgmm.n_components):
    y = np.exp(bgmm.score_samples(x))
    plt.fill_between(x[:, 0], 0, y, alpha=0.3)

plt.title('Bayesian Gaussian Mixture Model for 1D Data')
plt.xlabel('X')
plt.ylabel('Density')
plt.show()
