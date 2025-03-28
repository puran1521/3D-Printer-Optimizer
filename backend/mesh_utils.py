# backend/mesh_utils.py
"""
Utility functions for handling STL mesh files.
Includes voxelization and preprocessing.
"""

import trimesh
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MeshHandler:
    @staticmethod
    def load_and_voxelize(stl_path, nx, ny, nz):
        """
        Load an STL file and convert it into a voxel representation.

        Args:
            stl_path: Path to the STL file
            nx, ny, nz: Number of elements in each direction
        
        Returns:
            np.ndarray: 3D voxel grid representation of the model
        """
        try:
            mesh = trimesh.load_mesh(stl_path)
            voxels = mesh.voxelized(pitch=1 / nx)
            return voxels.matrix.astype(float)
        except Exception as e:
            logger.error(f"Error loading STL file {stl_path}: {e}")
            return None
