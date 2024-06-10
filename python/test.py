import numpy as np
from scipy.linalg import eigh

# Define the mass (M) and stiffness (K) matrices
# Example: A 2-degree-of-freedom system
M = np.array([[2.0, 0.0],
              [0.0, 1.0]])

K = np.array([[6.0, -2.0],
              [-2.0, 4.0]])

# Solve the generalized eigenvalue problem Kx = λMx
eigenvalues, eigenvectors = eigh(K, M)

# Eigenfrequencies are the square roots of the eigenvalues
eigenfrequencies = np.sqrt(eigenvalues)

# Sort the eigenfrequencies and corresponding eigenvectors
idx = np.argsort(eigenfrequencies)
eigenfrequencies = eigenfrequencies[idx]
eigenvectors = eigenvectors[:, idx]

# Display the results
print("Eigenfrequencies (rad/s):")
print(eigenfrequencies)

print("\nEigenvectors (mode shapes):")
print(eigenvectors)
