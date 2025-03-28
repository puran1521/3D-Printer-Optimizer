import numpy as np
import pytest
from ..fem import FEMSolver

@pytest.fixture
def fem_solver():
    """Create a FEM solver instance for testing"""
    return FEMSolver()

def test_compute_stiffness_matrix(fem_solver):
    """Test the fundamental properties of FEM stiffness matrix"""
    # Material properties
    E = 1.0  # Young's modulus (normalized)
    nu = 0.3  # Poisson's ratio
    
    # Compute stiffness matrix
    K = fem_solver.compute_stiffness_matrix(E, nu)
    
    # Test matrix properties
    assert isinstance(K, np.ndarray)
    assert K.shape == (24, 24)  # 3D element has 8 nodes × 3 DOF
    assert np.allclose(K, K.T)  # Symmetry check
    
    # Check positive semi-definiteness
    eigenvals = np.linalg.eigvals(K)
    assert np.all(eigenvals >= -1e-10)  # Allow for numerical precision

def test_assemble_global_matrix():
    """Check that the global stiffness matrix assembles correctly."""
    densities = np.ones(10)
    KE = np.eye(2)
    K = FEMSolver.assemble_global_matrix(densities, 1.0, KE, 3.0)
    assert K.shape[0] == 20  # Should match 2 * number of elements
