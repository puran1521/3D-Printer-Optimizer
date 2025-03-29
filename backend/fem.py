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
        """Compute element stiffness matrix for 3D 8-node brick element."""
        D = E / ((1 + nu) * (1 - 2 * nu)) * np.array([
            [1 - nu, nu, nu, 0, 0, 0],
            [nu, 1 - nu, nu, 0, 0, 0],
            [nu, nu, 1 - nu, 0, 0, 0],
            [0, 0, 0, (1 - 2 * nu) / 2, 0, 0],
            [0, 0, 0, 0, (1 - 2 * nu) / 2, 0],
            [0, 0, 0, 0, 0, (1 - 2 * nu) / 2]
        ])

        K = np.zeros((24, 24))
        gp = [-1/np.sqrt(3), 1/np.sqrt(3)]

        for i in gp:
            for j in gp:
                for k in gp:
                    B = self._compute_B_matrix(i, j, k)
                    K += B.T @ D @ B

        return K

    def _compute_B_matrix(self, xi: float, eta: float, zeta: float) -> np.ndarray:
        """Compute B matrix for strain-displacement relationship."""
        dN = np.array([
            [-0.125 * (1 - eta) * (1 - zeta), -0.125 * (1 - xi) * (1 - zeta), -0.125 * (1 - xi) * (1 - eta)],
            [ 0.125 * (1 - eta) * (1 - zeta), -0.125 * (1 + xi) * (1 - zeta), -0.125 * (1 + xi) * (1 - eta)],
            [ 0.125 * (1 + eta) * (1 - zeta),  0.125 * (1 + xi) * (1 - zeta), -0.125 * (1 + xi) * (1 + eta)],
            [-0.125 * (1 + eta) * (1 - zeta),  0.125 * (1 - xi) * (1 - zeta), -0.125 * (1 - xi) * (1 + eta)],
            [-0.125 * (1 - eta) * (1 + zeta), -0.125 * (1 - xi) * (1 + zeta),  0.125 * (1 - xi) * (1 - eta)],
            [ 0.125 * (1 - eta) * (1 + zeta), -0.125 * (1 + xi) * (1 + zeta),  0.125 * (1 + xi) * (1 - eta)],
            [ 0.125 * (1 + eta) * (1 + zeta),  0.125 * (1 + xi) * (1 + zeta),  0.125 * (1 + xi) * (1 + eta)],
            [-0.125 * (1 + eta) * (1 + zeta),  0.125 * (1 - xi) * (1 + zeta),  0.125 * (1 - xi) * (1 + eta)]
        ])
        B = np.zeros((6, 24))
        for i in range(8):
            B[0, i*3] = dN[i, 0]
            B[1, i*3+1] = dN[i, 1]
            B[2, i*3+2] = dN[i, 2]
            B[3, i*3] = dN[i, 1]
            B[3, i*3+1] = dN[i, 0]
            B[4, i*3+1] = dN[i, 2]
            B[4, i*3+2] = dN[i, 1]
            B[5, i*3] = dN[i, 2]
            B[5, i*3+2] = dN[i, 0]
        return B

    @staticmethod
    def solve_system(K, F, free_dofs):
        """Solve the system of equations K * U = F using sparse matrix techniques."""
        try:
            K_free = K[free_dofs, :][:, free_dofs]
            F_free = F[free_dofs]
            logger.info(f"K_free shape: {K_free.shape}, F_free shape: {F_free.shape}")
            if sp.linalg.norm(K_free, ord=2) == 0 or np.linalg.matrix_rank(K_free.toarray()) < K_free.shape[0]:
                raise ValueError("Global stiffness matrix is singular. Check boundary conditions or assembly.")
            U_free = spla.spsolve(K_free, F_free)
            U = np.zeros(K.shape[0])
            U[free_dofs] = U_free
            return U
        except MemoryError as e:
            logger.error(f"Memory error while solving FEM system: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error solving FEM system: {e}", exc_info=True)
            return None