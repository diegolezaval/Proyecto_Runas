// Fuerza, flujo FV y avance libre del paso 2, sin copiar su definición.
#include "../paso2_20261117/radial.c"

static double envolvente(double t) {
    if (t <= 0. || t >= 8.) return 0.;
    const double s = sin(3.14159265358979323846*t/8.);
    return s*s*sin(2.3*t);
}

// Verlet original con la aceleración externa de chi en cada extremo del paso.
// forma y peso sólo cubren las celdas de la fuente. peso = 4*pi*w*forma.
void advance_source(int n, int steps, int start, double dt, double dx,
                    const double *lo, const double *hi, const double *theta,
                    double *q, double *v, double *integrals, int ns,
                    const double *forma, const double *peso, double A, double *work) {
    const int stride = n+2, count = 3*stride, z0 = 2*stride+1;
    const int faces[2] = {(int)lround(40./dx), (int)lround(60./dx)};
    const double conduct[2] = {1600./dx, 3600./dx};
    double acc[count], previous[6], current[6];
    for (int k=0; k<count; ++k) acc[k]=0.;
    force(n,lo,hi,theta,q,acc);
    double j0 = A*envolvente(start*dt);
    for (int k=0; k<ns; ++k) acc[z0+k] += j0*forma[k];
    for (int k=0; k<2; ++k) flux(stride,faces[k],conduct[k],q,v,previous+3*k);
    for (int step=0; step<steps; ++step) {
        for (int k=0; k<count; ++k) {
            v[k] += .5*dt*acc[k];
            q[k] += dt*v[k];
        }
        const double j1=A*envolvente((start+step+1)*dt);
        double suma=0.;
        for (int k=0; k<ns; ++k) suma+=peso[k]*v[z0+k];
        *work += .5*(j0+j1)*dt*suma;
        force(n,lo,hi,theta,q,acc);
        for (int k=0; k<ns; ++k) acc[z0+k] += j1*forma[k];
        for (int k=0; k<count; ++k) v[k] += .5*dt*acc[k];
        for (int k=0; k<2; ++k) flux(stride,faces[k],conduct[k],q,v,current+3*k);
        for (int k=0; k<6; ++k) {
            integrals[k] += .5*dt*(previous[k]+current[k]);
            previous[k]=current[k];
        }
        j0=j1;
    }
}
