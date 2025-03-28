import pytest
import numpy as np
from backend.mesh_utils import MeshHandler

def test_load_and_voxelize(mocker):
    """Ensure STL files are loaded and voxelized correctly."""
    mock_mesh = mocker.patch("trimesh.load_mesh")
    mock_voxels = mocker.MagicMock()
    mock_voxels.matrix = np.ones((5, 5, 5))
    mock_mesh.return_value.voxelized.return_value = mock_voxels

    mesh_handler = MeshHandler()
    voxel_data = mesh_handler.load_and_voxelize("mock.stl", 5, 5, 5)
    assert voxel_data.shape == (5, 5, 5)
    assert np.all(voxel_data == 1)
