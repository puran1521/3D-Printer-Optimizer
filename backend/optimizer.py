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

    def _perform_fem_analysis(self, voxel_grid, nodes, elements, KE):
        K = self.assemble_global_matrix(voxel_grid, nodes, elements, KE, self.config.penal)
        if K is None:
            logger.error("Failed to assemble global stiffness matrix")
            return None
        logger.info(f"Global stiffness matrix K shape: {K.shape}")
        # ... rest of the function

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
            
            # Convert elements to numpy array and check its validity
            elements = np.asarray(elements)
            if elements.size == 0:
                raise ValueError("Empty elements array")
                
            logger.debug(f"densities shape: {densities.shape}")
            logger.debug(f"nodes shape: {nodes.shape}")
            logger.debug(f"elements shape: {elements.shape}")
            logger.debug(f"KE shape: {KE.shape}")

            ndof = len(nodes) * 3
            global_matrix = lil_matrix((ndof, ndof))

            for element_index, element_nodes in enumerate(elements):
                # Get coordinates more safely
                node_coords = nodes[element_nodes]
                center = node_coords.mean(axis=0)
                
                # Convert to integer indices more safely
                coords = np.floor(center).astype(int)
                coords = np.clip(coords, 0, 
                               [densities.shape[0]-1, 
                                densities.shape[1]-1, 
                                densities.shape[2]-1])
                logger.debug(f"Clipped coords: {coords}")

                # Debug current element
                if element_index % 1000 == 0:
                    logger.debug(f"Processing element {element_index}")
                    logger.debug(f"Element coords: {coords}")

                # Get density and assemble matrix
                element_density = densities[coords[0], coords[1], coords[2]]
                logger.debug(f"element_density: {element_density}")
                element_dofs = []
                for node in element_nodes:
                    element_dofs.extend([3*node, 3*node + 1, 3*node + 2])
                element_dofs = np.array(element_dofs)
                
                logger.debug(f"Element DOFs: {element_dofs}")
                logger.debug(f"Global matrix shape: {global_matrix.shape}")
                logger.debug(f"KE shape: {KE.shape}")
                logger.debug(f"Element density: {element_density}")

                if np.any(element_dofs >= global_matrix.shape[0]):
                    logger.error(f"Invalid DOFs: {element_dofs}")
                    raise ValueError("DOFs exceed global matrix dimensions")
                if np.any(element_dofs < 0):
                    logger.error(f"Negative DOFs: {element_dofs}")
                    raise ValueError("DOFs contain negative indices")
                if KE.shape[0] != KE.shape[1] or KE.shape[0] != len(element_dofs):
                    logger.error(f"Invalid KE shape: {KE.shape} for DOFs: {len(element_dofs)}")
                    raise ValueError("KE dimensions do not match DOFs")

                logger.debug(f"element_index: {element_index}")
                logger.debug(f"element_nodes: {element_nodes}")
                logger.debug(f"element_density: {element_density}")
                logger.debug(f"KE: {KE}")

                # Add contribution
                try:
                    global_matrix[np.ix_(element_dofs, element_dofs)] += KE * (element_density**penal)
                except Exception as e:
                    logger.error(f"Error updating global matrix: {e}", exc_info=True)
                    raise

            return global_matrix.tocsr()

        except Exception as e:
            logger.error(f"Error assembling global matrix: {e}", exc_info=True)
            return None