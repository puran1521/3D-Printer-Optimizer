import numpy as np
from typing import Optional, Callable
from .config import OptimizationConfig
from .mesh_utils import MeshHandler
from .fem import FEMSolver, FEMResult
import logging
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

logger = logging.getLogger(__name__)

class TopologyOptimizer:
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.mesh_handler = MeshHandler()
        self.fem_solver = FEMSolver()

    def optimize(self, stl_path: str, callback: Optional[Callable] = None) -> np.ndarray:
        try:
            logger.info("Starting optimization process...")
            voxel_grid, nodes, elements = self.mesh_handler.load_and_voxelize(stl_path, voxel_size=1.0)
            if voxel_grid is None or nodes is None or elements is None:
                raise RuntimeError("Failed to load mesh and voxelize")
            KE = self.fem_solver.compute_stiffness_matrix(self.config.E1, self.config.nu)
            logger.info(f"Element stiffness matrix KE shape: {KE.shape}")

            change = float('inf')
            iteration = 0

            while change > self.config.tol and iteration < self.config.max_iter:
                densities_old = voxel_grid.copy()
                U = self._perform_fem_analysis(voxel_grid, nodes, elements, KE)
                if U is None:
                    raise RuntimeError("FEM analysis failed")

                dc = self._compute_sensitivities(voxel_grid, U, KE)
                voxel_grid = self._update_densities(dc, voxel_grid)

                change = np.max(np.abs(voxel_grid - densities_old))
                logger.info(f"Iteration {iteration}: change = {change:.6f}")
                if callback:
                    callback(iteration, voxel_grid, change)
                if change < self.config.tol:
                    logger.info("Convergence reached.")
                    break
                iteration += 1

            logger.info("Optimization completed successfully")
            return voxel_grid
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise RuntimeError(f"Optimization failed: {e}")

    def _perform_fem_analysis(self, voxel_grid, nodes, elements, KE: np.ndarray) -> np.ndarray:
        try:
            logger.info("Starting FEM analysis...")
            K = self.assemble_global_matrix(voxel_grid, nodes, elements, KE, self.config.penal)
            logger.info(f"Global stiffness matrix K shape: {K.shape}")
            if K is None:
                raise ValueError("Global stiffness matrix assembly failed.")

            ndof = len(nodes) * 3
            F = np.zeros(ndof)
            F[300] = -1.0
            logger.info(f"Force vector F shape: {F.shape}")

            fixed_dofs = [0, 1, 2] # Example: Fix the first node in all three directions
            if len(fixed_dofs) < 3:
                logger.warning("Insufficient boundary conditions. Ensure at least 3 DOFs are fixed.")
            free_dofs = list(set(range(ndof)) - set(fixed_dofs))
            logger.info(f"Free DOFs: {len(free_dofs)}, Fixed DOFs: {len(fixed_dofs)}")

            U = self.fem_solver.solve_system(K, F, free_dofs)
            if U is None or np.isnan(U).any():
                raise RuntimeError("Displacement vector contains invalid values.")

            logger.info(f"Displacement vector U computed successfully.")
            return U
        except Exception as e:
            logger.error(f"FEM analysis failed: {e}", exc_info=True)
            return None

    def _compute_sensitivities(self, densities: np.ndarray, U: np.ndarray, KE: np.ndarray) -> np.ndarray:
        try:
            dc = -densities * np.sum(U**2)
            return dc
        except Exception as e:
            logger.error(f"Sensitivity analysis failed: {e}")
            return np.zeros_like(densities)

    def _update_densities(self, dc: np.ndarray, densities: np.ndarray) -> np.ndarray:
        try:
            move = 0.2
            l1 = 0
            l2 = 1e9
            target_vol = self.config.volfrac * densities.size

            while (l2 - l1) > 1e-4:
                lmid = 0.5 * (l2 + l1)
                new_densities = np.maximum(0.001, np.maximum(
                    densities - move,
                    np.minimum(1.0, np.minimum(
                        densities + move,
                        densities * np.sqrt(np.maximum(0, -dc / lmid))
                    ))
                ))
                if np.sum(new_densities) - target_vol > 0:
                    l1 = lmid
                else:
                    l2 = lmid
            return new_densities
        except Exception as e:
            logger.error(f"Density update failed: {e}")
            return densities

    def assemble_global_matrix(self, densities, nodes, elements, KE, penal):
        try:
            logger.info("Assembling global stiffness matrix...")
            ndof = len(nodes) * 3
            global_matrix = lil_matrix((ndof, ndof))

            for element_index, element_nodes in enumerate(elements):
                element_dofs = np.array(element_nodes) * 3
                element_dofs = np.concatenate([element_dofs, element_dofs + 1, element_dofs + 2])
                global_matrix[np.ix_(element_dofs, element_dofs)] += KE * densities[element_nodes[0]//1,element_nodes[0]//1,element_nodes[0]//1]**penal

            return global_matrix.tocsr()
        except Exception as e:
            logger.error(f"Error assembling global matrix: {e}", exc_info=True)
            return None