"""Geometría racional y cotas de Bézier; sólo biblioteca estándar."""
from fractions import Fraction as F
import math

def transform(inst,p):
 a,b,tx,ty=map(F,inst['transform_fraction']);x,y=map(lambda v:F(str(v)),p)
 return a*x-b*y+tx,b*x+a*y+ty

def ends(g,r):return {i['id']+'.'+e:transform(i,p) for i in r['instances'] for e,p in g['source_pieces'][i['piece']]['ends'].items()}

def segments(g,r):return [(i['id'],[transform(i,p) for p in seg]) for i in r['instances'] for seg in g['source_pieces'][i['piece']]['segments']]

def curveval(p,t):
 if len(p)==2:return tuple(float(p[0][k])*(1-t)+float(p[1][k])*t for k in (0,1))
 return tuple(sum(float(p[j][k])*[ (1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3][j] for j in range(4)) for k in (0,1))

def bounds(g,r):
 pts=[]
 for _,p in segments(g,r):
  ts=[0,1]
  if len(p)==4:
   for k in (0,1):
    p0,p1,p2,p3=[float(v[k]) for v in p];a=-p0+3*p1-3*p2+p3;b=2*(p0-2*p1+p2);c=p1-p0
    if abs(a)<1e-14:
     if abs(b)>1e-14:ts.append(-c/b)
    elif b*b-4*a*c>=0:
     d=math.sqrt(b*b-4*a*c);ts.extend([(-b+d)/(2*a),(-b-d)/(2*a)])
  pts.extend(curveval(p,t) for t in ts if 0<=t<=1)
 return min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)

def topology(g,r):
 ep=ends(g,r);parents={e:e for e in ep};parents.update({i['id']:i['id'] for i in r['instances']})
 def find(x):
  while parents[x]!=x:x=parents[x]
  return x
 def union(a,b):parents[find(a)]=find(b)
 for j in r['joins']:
  for e in j[1:]:union(j[0],e)
 V=len(set(find(e) for e in parents));E=len(ep)
 for e in ep:union(e.split('.')[0],e)
 C=len(set(find(e) for e in parents))
 return {'pieces':len(r['instances']),'endpoints':len(ep),'joins':len(r['joins']),'connected_components':C,'independent_cycles':E-V+C,'free_ends':len(r['free_ends'])}

def straight_overlaps(g,r):
 ss=[(i,p) for i,p in segments(g,r) if len(p)==2];out=[]
 def cross(a,b):return a[0]*b[1]-a[1]*b[0]
 def sub(a,b):return a[0]-b[0],a[1]-b[1]
 for k,(i,p) in enumerate(ss):
  for j,q in ss[k+1:]:
   if i==j:continue
   v=sub(p[1],p[0]);w=sub(q[1],q[0])
   if cross(v,w)!=0 or cross(v,sub(q[0],p[0]))!=0:continue
   d=0 if v[0] else 1
   lo=max(min(p[0][d],p[1][d]),min(q[0][d],q[1][d]));hi=min(max(p[0][d],p[1][d]),max(q[0][d],q[1][d]))
   if hi>lo:out.append([i,j])
 return out
