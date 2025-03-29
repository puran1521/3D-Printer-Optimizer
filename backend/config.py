# backend/config.py
"""
Configuration file for optimization settings.
Defines key parameters used in topology optimization.
"""

class OptimizationConfig:
    def __init__(self, nelx=50, nely=50, nelz=37, volfrac=0.4, penal=3.0, rmin=1.5, E1=1.0, E2=1e-9, nu=0.3, tol=1e-3, max_iter=100):
        self.nelx = nelx
        self.nely = nely
        self.nelz = nelz
        self.volfrac = volfrac
        self.penal = penal
        self.rmin = rmin
        self.E1 = E1
        self.E2 = E2
        self.nu = nu
        self.tol = tol
        self.max_iter = max_iter

    def __repr__(self):
        return (f"OptimizationConfig(nelx={self.nelx}, nely={self.nely}, nelz={self.nelz}, "
                f"volfrac={self.volfrac}, penal={self.penal}, rmin={self.rmin}, E1={self.E1}, "
                f"E2={self.E2}, nu={self.nu}, tol={self.tol}, max_iter={self.max_iter})")
