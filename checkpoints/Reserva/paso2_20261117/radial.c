// Evolución radial M2. Las matrices q, v y acc tienen tres filas con dos halos nulos.
#include <math.h>
#include <stddef.h>

static void force(int n, const double *lo, const double *hi, const double *theta,
                  const double *q, double *acc) {
    const int stride = n + 2;
    const double *a=q, *b=q+stride, *z=q+2*stride;
    for (int i=1; i<=n; ++i) {
        double density = a[i]*a[i] + b[i]*b[i];
        double local = theta[0] + 2*theta[2]*density + theta[3]*z[i] + .5*theta[4]*z[i]*z[i];
        acc[i] = hi[i-1]*(a[i+1]-a[i]) - lo[i-1]*(a[i]-a[i-1]) - local*a[i];
        acc[stride+i] = hi[i-1]*(b[i+1]-b[i]) - lo[i-1]*(b[i]-b[i-1]) - local*b[i];
        acc[2*stride+i] = hi[i-1]*(z[i+1]-z[i]) - lo[i-1]*(z[i]-z[i-1])
                           - (theta[1]+theta[4]*density)*z[i] - theta[3]*density;
    }
}

// Flujo saliente exacto en tiempo continuo de la acción FV con media energía de cara.
static void flux(int stride, int face, double conduct, const double *q,
                 const double *v, double *out) {
    const int i=face, j=i+1;
    const double area = 12.56637061435917295385 * conduct;
    double work=0;
    for (int field=0; field<3; ++field) {
        int off=field*stride;
        work += (field==2 ? .5 : 1.)*(v[off+i]+v[off+j])*(q[off+j]-q[off+i]);
    }
    out[0] = -area*work;
    out[1] = -2*area*(q[i]*q[stride+j]-q[stride+i]*q[j]);
    out[2] = fmax(0.,out[0]);
}

void advance(int n, int steps, double dt, double dx, const double *lo, const double *hi,
             const double *theta, double *q, double *v, double *integrals) {
    const int stride=n+2, count=3*stride;
    double acc[count], previous[6], current[6];
    for (int j=0;j<count;++j) acc[j]=0.;
    int faces[2]={(int)lround(40./dx),(int)lround(60./dx)};
    double conduct[2]={1600./dx,3600./dx};
    force(n,lo,hi,theta,q,acc);
    for (int j=0;j<2;++j) flux(stride,faces[j],conduct[j],q,v,previous+3*j);
    for (int step=0;step<steps;++step) {
        for (int j=0;j<count;++j) {
            v[j] += .5*dt*acc[j];
            q[j] += dt*v[j];
        }
        force(n,lo,hi,theta,q,acc);
        for (int j=0;j<count;++j) v[j] += .5*dt*acc[j];
        for (int j=0;j<2;++j) flux(stride,faces[j],conduct[j],q,v,current+3*j);
        for (int j=0;j<6;++j) {
            integrals[j] += .5*dt*(previous[j]+current[j]);
            previous[j]=current[j];
        }
    }
}
