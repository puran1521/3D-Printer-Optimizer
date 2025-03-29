# backend/fem.py
"""
Finite Element Method (FEM) Solver for topology optimization.
Handles stiffness matrix computation and system solving.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import logging

logger = logging.getLogger(__name__)

class FEMResult:
    def __init__(self, displacements, stresses):
        self.displacements = displacements
        self.stresses = stresses

class FEMSolver:
    def compute_stiffness_matrix(self, E: float, nu: float) -> np.ndarray:
        """
        Compute element stiffness matrix for 3D 8-node brick element.
        
        Args:
            E: Young's modulus
            nu: Poisson's ratio
            
        Returns:
            np.ndarray: 24x24 element stiffness matrix
        """
        # Define material matrix D
        D = E / ((1 + nu) * (1 - 2 * nu)) * np.array([
            [1 - nu, nu, nu, 0, 0, 0],
            [nu, 1 - nu, nu, 0, 0, 0],
            [nu, nu, 1 - nu, 0, 0, 0],
            [0, 0, 0, (1 - 2 * nu) / 2, 0, 0],
            [0, 0, 0, 0, (1 - 2 * nu) / 2, 0],
            [0, 0, 0, 0, 0, (1 - 2 * nu) / 2]
        ])

        # Initialize 24x24 stiffness matrix
        K = np.zeros((24, 24))
        
        # Gauss quadrature points
        gp = [-1/np.sqrt(3), 1/np.sqrt(3)]
        
        # Precompute B matrices for each integration point
        for i in gp:
            for j in gp:
                for k in gp:
                    B = self._compute_B_matrix(i, j, k)  # Should be vectorized if possible
                    K += B.T @ D @ B
                    
        return K
    
    def _compute_B_matrix(self, xi: float, eta: float, zeta: float) -> np.ndarray:
        """Compute B matrix for strain-displacement relationship."""
        dN = np.random.rand(8, 3)  # Placeholder for shape function derivatives
        B = np.zeros((6, 24))
        for i in range(8):
            B[0, i*3] = dN[i, 0]
            B[1, i*3+1] = dN[i, 1]
            B[2, i*3+2] = dN[i, 2]
        return B

    @staticmethod
    def assemble_global_matrix(densities, E1, KE, penal):
        """
        Assemble the global stiffness matrix.

        Args:
            densities: Element densities
            E1: Young's modulus
            KE: Element stiffness matrix
            penal: Penalization factor
        
        Returns:
            scipy.sparse matrix: Global stiffness matrix
        """
        try:
            size = densities.size * KE.shape[0]
            K = sp.lil_matrix((size, size))
            
            for i in range(densities.size):
                K[i:i+2, i:i+2] += (E1 * densities[i] ** penal) * KE

            return K.tocsr()
        except Exception as e:
            logger.error(f"Error assembling global matrix: {e}")
            return None

    @staticmethod
    def solve_system(K, F, free_dofs):
        """
        Solve the system of equations K * U = F.
        
        Args:
            K: Global stiffness matrix
            F: Force vector
            free_dofs: Indices of free degrees of freedom
        
        Returns:
            np.ndarray: Displacement vector
        """
        try:
            K_free = K[free_dofs, :][:, free_dofs]
            F_free = F[free_dofs]
            
            U = np.zeros(K.shape[0])
            U_free = spla.spsolve(K_free, F_free)
            U[free_dofs] = U_free
            
            return U
        except Exception as e:
            logger.error(f"Error solving FEM system: {e}")
            return None
    pass
