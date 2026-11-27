"""Contraste independiente del máximo cociente y la reconstrucción de carga."""
import csv
import json
import numpy as np
from scipy.sparse import bmat,csc_matrix
from scipy.sparse.linalg import splu,eigsh,LinearOperator
import energia as e

o=e.o
data=json.loads((e.HERE/"resultado.json").read_text())
rng=np.random.default_rng(271126)
def largest(base,comm,u,beta):
    vec=csc_matrix(u[:,None])
    aug=bmat([[base,vec],[vec.T,csc_matrix([[-1/beta]])]],format="csc")
    lu=splu(aug)
    def apply(x):
        return comm@lu.solve(np.r_[comm.T@x,0.])[:-1]
    op=LinearOperator(base.shape,matvec=apply)
    l,v=eigsh(op,k=1,which="LA",v0=rng.normal(size=len(u)),tol=1e-10)
    assert np.linalg.norm(apply(v[:,0])-l[0]*v[:,0])<1e-8
    return np.sqrt(l[0])

norms=[largest(o.A,e.JA,o.v,4*e.om**2),largest(o.P,e.J,o.u,1.)]
assert all(.35<x<.5 for x in norms)
# Campo manufacturado. La inversión del peso no se aplica a datos medidos.
a,b,p=rng.normal(size=(3,e.g.n))
y=e.s*b
assert np.linalg.norm(e.J@y-(o.T@y-e.s*(o.T@b)))<1e-8
u=o.u
physical=u@(p+2*e.om*a)
weighted=u@(e.s*(p+2*e.om*a))
assert abs(physical-(weighted+(u/e.s-u)@(e.s*(p+2*e.om*a))))<1e-13
# El aporte de las dos fuerzas cinéticas y de la energía de la cara interior
# se cancela al derivar la energía total de esa cara, de peso plano.
i=e.loc.i40
grad=b[i]-b[i-1]
exchange=e.loc.face[i-1]*grad*(p[i-1]-p[i]+p[i]-p[i-1])
assert abs(exchange)<1e-9 and e.s[i-1]==e.s[i]==1
with (e.HERE/"envolventes.csv").open() as stream:
    rows=list(csv.DictReader(stream))
assert len(rows)==960 and e.loc.ref.sha(e.HERE/"envolventes.csv")==data["sha_csv"]
for case in data["casos"]:
    seq=[r for r in rows if r["caso"]==case["caso"]]
    assert [float(r["t"]) for r in seq]==[j/8 for j in range(1,321)]
    for col,key in (("temporal","integral_temporal"),("Taylor","integral_Taylor")):
        assert abs(sum(float(r[col]) for r in seq)/8-case[key])<1e-12
print("Normas por resolución bordeada:",norms,"· 960 filas y carga verificadas")
