"""Accion M2 con cinco coordenadas independientes y unidades explicitas.

La normalizacion es una eleccion de unidades; no se reajusta para conseguir
un observable. Las formulas valen tambien fuera de la subfamilia sextica.
"""
from dataclasses import dataclass, replace
from pathlib import Path
import json
import numpy as np

@dataclass(frozen=True)
class ScalarModel:
    m: float
    M: float
    lambda0: float
    g: float
    h: float
    mass_reference: float = 1.0
    lambda_reference: float = .001

    @property
    def derived_lambda(self):return self.g**2/(2*self.M**2)-self.lambda0
    @property
    def mass2(self):return (self.m/self.mass_reference)**2
    @property
    def mediator(self):return self.M/self.mass_reference
    @property
    def quartic(self):return self.lambda0/self.lambda_reference
    @property
    def trilinear(self):return self.g/(self.mass_reference*np.sqrt(self.lambda_reference))
    @property
    def mixed(self):return self.h/self.lambda_reference

    def potential(self,f,z):
        return self.mass2*f*f+self.quartic*f**4+.5*self.mediator**2*z*z+self.trilinear*z*f*f+.5*self.mixed*z*z*f*f

    def effective(self,s):
        return self.mass2*s+self.quartic*s*s-self.trilinear**2*s*s/(2*(self.mediator**2+self.mixed*s))

    def effective_prime(self,s):
        D=self.mediator**2+self.mixed*s
        return self.mass2+2*self.quartic*s-.5*self.trilinear**2*s*(2*self.mediator**2+self.mixed*s)/D**2

    def effective_second(self,s):
        return 2*self.quartic-self.trilinear**2*self.mediator**4/(self.mediator**2+self.mixed*s)**3

    def forces(self,f,z,omega=0):
        """Radial RHS without the geometric Laplacian terms."""
        return ((self.mass2-omega**2+2*self.quartic*f*f+self.trilinear*z+.5*self.mixed*z*z)*f,
                (self.mediator**2+self.mixed*f*f)*z+self.trilinear*f*f)

    def amplitude_jacobian(self,f,z,omega=0):
        return np.array([[self.mass2-omega**2+6*self.quartic*f*f+self.trilinear*z+.5*self.mixed*z*z,
                          f*(self.trilinear+self.mixed*z)],
                         [2*f*(self.trilinear+self.mixed*z),self.mediator**2+self.mixed*f*f]])

    def coexistence(self):
        """Analytic minimum of U(s)/s for lambda0,h,M>0 and attraction."""
        if min(self.lambda0,self.h,self.M,self.m)<=0 or self.derived_lambda<=0:
            raise ValueError('Outside the admitted attractive positive-quartic sector')
        s_physical=(abs(self.g)*self.M/np.sqrt(2*self.lambda0)-self.M**2)/self.h
        mu2=self.m**2-(abs(self.g)-np.sqrt(2*self.lambda0)*self.M)**2/(2*self.h)
        return dict(s=s_physical*self.lambda_reference/self.mass_reference**2,
                    omega_squared=mu2/self.mass_reference**2,
                    vacuum_coercivity_margin_physical=mu2)

    def with_parameter(self,name,value):
        if name not in ('m','M','lambda0','g','h'):raise ValueError(name)
        return replace(self,**{name:float(value)})

ROOT=Path(__file__).resolve().parents[1]
THETA=json.loads((ROOT/'datos/theta_comun.json').read_text())
def from_config(config=THETA):
    b=config['scalar_benchmark'];p=b['fundamental_natural_units'];u=b['normalization']
    return ScalarModel(**{k:p[k] for k in ('m','M','lambda0','g','h')},
                       mass_reference=u['mass_reference_eV'],lambda_reference=u['lambda_reference'])
BENCHMARK=from_config()

def require_reference_benchmark():
    """Legacy reductions contain benchmark-specific analytic formulas."""
    expected={'m':1.,'M':100.,'lambda0':.099,'g':44.721359549995796,'h':.1}
    if any(not np.isclose(getattr(BENCHMARK,k),v,rtol=1e-13,atol=0) for k,v in expected.items()):
        raise ValueError('Los scripts historicos son del benchmark 4.1. Para variar Theta use ScalarModel y soluciones_m2; regenere las reducciones afectadas.')
