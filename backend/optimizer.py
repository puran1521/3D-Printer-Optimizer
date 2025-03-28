import numpy as np
from typing import Optional, Callable
from .config import OptimizationConfig
from .mesh_utils import MeshHandler
from .fem import FEMSolver, FEMResult
import logging

logger = logging.getLogger(__name__)

class TopologyOptimizer:
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """Initialize topology optimizer with configuration."""
        self.config = config or OptimizationConfig()
        self.mesh_handler = MeshHandler()
        self.fem_solver = FEMSolver()
        
    def optimize(self, stl_path: str, callback: Optional[Callable] = None) -> np.ndarray:
        """Main optimization loop."""
        try:
            logger.info("Starting optimization process...")
            densities = self.mesh_handler.load_and_voxelize(
                stl_path, self.config.nelx, self.config.nely, self.config.nelz
            )
            KE = self.fem_solver.compute_stiffness_matrix(
                self.config.E1, self.config.nu
            )
            
            change = float('inf')
            iteration = 0
            
            while change > self.config.tol and iteration < self.config.max_iter:
                densities_old = densities.copy()
                U = self._perform_fem_analysis(densities, KE)
                if U is None:
                    raise RuntimeError("FEM analysis failed")
                
                dc = self._compute_sensitivities(densities, U, KE)
                densities = self._update_densities(dc, densities)
                
                change = np.max(np.abs(densities - densities_old))
                logger.info(f"Iteration {iteration}: change = {change:.6f}")
                if callback:
                    callback(iteration, densities, change)
                
                iteration += 1
            
            logger.info("Optimization completed successfully")
            return densities
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            raise RuntimeError(f"Optimization failed: {str(e)}")

    def _perform_fem_analysis(self, densities: np.ndarray, KE: np.ndarray) -> np.ndarray:
        """Perform FEM analysis step."""
        try:
            K = self.fem_solver.assemble_global_matrix(
                densities, self.config.E1, KE, self.config.penal
            )
            ndof = 3 * (self.config.nelx + 1) * (self.config.nely + 1) * (self.config.nelz + 1)
            F = np.zeros(ndof)
            fixed_dofs = []
            free_dofs = list(set(range(ndof)) - set(fixed_dofs))
            U = self.fem_solver.solve_system(K, F, free_dofs)
            return U
        except Exception as e:
            logger.error(f"FEM analysis failed: {str(e)}")
            return None

    def _compute_sensitivities(self, densities: np.ndarray, U: np.ndarray, KE: np.ndarray) -> np.ndarray:
        """Compute sensitivity analysis."""
        try:
            dc = np.zeros_like(densities)
            return dc
        except Exception as e:
            logger.error(f"Sensitivity analysis failed: {str(e)}")
            return np.zeros_like(densities)

    def _update_densities(self, dc: np.ndarray, densities: np.ndarray) -> np.ndarray:
        """Update densities using the Optimality Criteria method."""
        try:
            move = 0.2
            l1 = 0
            l2 = 1e9
            vol = np.sum(densities)
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
            logger.error(f"Density update failed: {str(e)}")
            return densities