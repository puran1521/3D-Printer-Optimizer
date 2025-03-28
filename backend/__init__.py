# backend/__init__.py
"""
Initialization file for the backend module.
Ensures that all dependencies and configurations are properly loaded.
"""

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from .config import OptimizationConfig
from .optimizer import TopologyOptimizer
from .fem import FEMSolver
from .mesh_utils import MeshHandler
