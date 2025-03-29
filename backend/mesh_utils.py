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
    def load_and_voxelize(stl_path, voxel_size=1.0):
        try:
            logger.info(f"Loading STL file: {stl_path}")
            mesh = trimesh.load(stl_path)
            logger.info(f"Loaded mesh vertices: {len(mesh.vertices)}, faces: {len(mesh.faces)}")

            logger.info(f"Voxelizing mesh with voxel size: {voxel_size}")
            voxels = mesh.voxelized(voxel_size)
            logger.info(f"Voxel grid shape: {voxels.shape}")

            voxel_matrix = voxels.matrix
            nodes, elements = MeshHandler.voxel_to_nodes_elements(voxel_matrix, voxel_size)

            return voxel_matrix, nodes, elements

        except Exception as e:
            logger.error(f"Error loading STL file {stl_path}: {e}", exc_info=True)
            return None, None, None

    @staticmethod
    def voxel_to_nodes_elements(voxel_matrix, voxel_size):
        nodes = []
        elements = []
        node_index = 0
        element_index = 0

        for x in range(voxel_matrix.shape[0] - 1):
            for y in range(voxel_matrix.shape[1] - 1):
                for z in range(voxel_matrix.shape[2] - 1):
                    if voxel_matrix[x,y,z]:
                        node_coords = [
                            [x, y, z],
                            [x + 1, y, z],
                            [x + 1, y + 1, z],
                            [x, y + 1, z],
                            [x, y, z + 1],
                            [x + 1, y, z + 1],
                            [x + 1, y + 1, z + 1],
                            [x, y + 1, z + 1],
                        ]
                        nodes.extend(node_coords)
                        elements.append(list(range(node_index, node_index + 8)))
                        node_index += 8
                        element_index += 1

        nodes = np.array(nodes) * voxel_size
        return nodes, elements