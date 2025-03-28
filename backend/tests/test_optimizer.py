import numpy as np
import pytest
from backend.optimizer import TopologyOptimizer
from backend.config import OptimizationConfig

@pytest.fixture
def optimizer():
    config = OptimizationConfig(nelx=10, nely=10, nelz=10)
    return TopologyOptimizer(config)

def test_optimizer_initialization(optimizer):
    """Ensure optimizer initializes with correct config values."""
    assert optimizer.config.nelx == 10
    assert optimizer.config.nely == 10
    assert optimizer.config.nelz == 10

def test_optimization_process(optimizer, mocker):
    """Simulate an optimization process and check output shape."""
    # Mock voxelization
    mocker.patch(
        "backend.mesh_utils.MeshHandler.load_and_voxelize",
        return_value=np.ones((10, 10, 10))
    )
    
    # Mock FEM analysis - needs correct matrix size
    mocker.patch(
        "backend.optimizer.TopologyOptimizer._perform_fem_analysis",
        return_value=np.zeros((1000, 1))  # 10x10x10 nodes
    )
    
    # Mock sensitivity analysis
    mocker.patch(
        "backend.optimizer.TopologyOptimizer._compute_sensitivities",
        return_value=np.ones((10, 10, 10))
    )

    # Run optimization
    densities = optimizer.optimize("mock_model.stl")
    assert densities.shape == (10, 10, 10)
