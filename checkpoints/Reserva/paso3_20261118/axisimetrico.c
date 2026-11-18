// Acción FV de M2 en anillos cilíndricos. Las matrices tienen un halo por lado.
#include <math.h>
#include <stddef.h>
typedef struct {
    int nr, nz;
    const double *rm, *rp, *zm, *zp, *vr, *vz, *wd, *wr, *theta;
    int ns;
    const int *ind;
    const double *forma, *dVsrc;
} Mesh;

static inline double lap(const Mesh *g, const double *u, int k, int i, int j) {
    const int s=g->nz+2;
    return g->rm[i]*(u[k-s]-u[k])+g->rp[i]*(u[k+s]-u[k])
         + g->zm[j]*(u[k-1]-u[k])+g->zp[j]*(u[k+1]-u[k]);
}

static inline double pulse(double t) {
    if (t <= 0. || t >= 8.) return 0.;
    double e=sin(3.14159265358979323846*t/8.);
    return e*e*sin(2.3*t);
}

// out puede contener q(n-1). Se lee esa misma celda antes de reemplazarla.
static void step(const Mesh *g, const double *restrict x, double *restrict out,
                 double dt2, double drive) {
    const int s=g->nz+2, n=(g->nr+2)*s;
    const double *a=x, *b=x+n, *c=x+2*n, *th=g->theta;
    double *pa=out, *pb=out+n, *pc=out+2*n;
    for (int i=0; i<g->nr; ++i) {
        const int start=(i+1)*s+1;
        #pragma omp simd
        for (int j=0; j<g->nz; ++j) {
            int k=start+j;
            double dens=a[k]*a[k]+b[k]*b[k], z=c[k];
            double local=th[0]+2.*th[2]*dens+th[3]*z+.5*th[4]*z*z;
            pa[k]=2.*a[k]-pa[k]+dt2*(lap(g,a,k,i,j)-local*a[k]);
            pb[k]=2.*b[k]-pb[k]+dt2*(lap(g,b,k,i,j)-local*b[k]);
            pc[k]=2.*z-pc[k]+dt2*(lap(g,c,k,i,j)-(th[1]+th[4]*dens)*z-th[3]*dens);
        }
    }
    if (drive!=0.) for (int m=0;m<g->ns;++m) pc[g->ind[m]]+=dt2*drive*g->forma[m];
}

// Verlet en posiciones. El número par de pasos devuelve q(n) en el primer búfer.
void avanzar(const Mesh *g, double *x, double *p, int nsteps, int start, double dt,
             double A, double *work) {
    const int n=(g->nr+2)*(g->nz+2);
    for (int k=0;k<nsteps;++k) {
        double drive=A*pulse((start+k)*dt);
        step(g,x,p,dt*dt,drive);
        if ((start+k)*dt < 8. && A!=0.) {
            double mid=.5*(drive+A*pulse((start+k+1)*dt)), sum=0.;
            const double *z=x+2*n, *next=p+2*n;
            for (int m=0;m<g->ns;++m) {
                int j=g->ind[m];
                sum+=g->dVsrc[m]*g->forma[m]*(next[j]-z[j]);
            }
            *work += mid*sum;
        }
        double *swap=x;x=p;p=swap;
    }
}

// Suma de H y Q, sin integrar exterior por diferencia de campos.
// mode=0 prepara q(n-1) desde (q,v); mode=1 reconstruye v; mode=2 sólo mide.
void observar(const Mesh *g, const double *x, double *p, double *vel, double dt,
              double drive, int mode, double *res) {
    const int s=g->nz+2, n=(g->nr+2)*s;
    const double *a=x,*b=x+n,*c=x+2*n,*th=g->theta;
    if (mode!=2) {
        for (int i=0;i<g->nr;++i) {
            #pragma omp simd
            for (int j=0;j<g->nz;++j) {
                int k=(i+1)*s+1+j;
                double dens=a[k]*a[k]+b[k]*b[k], z=c[k];
                double local=th[0]+2.*th[2]*dens+th[3]*z+.5*th[4]*z*z;
                const double acc[3]={lap(g,a,k,i,j)-local*a[k],lap(g,b,k,i,j)-local*b[k],
                                     lap(g,c,k,i,j)-(th[1]+th[4]*dens)*z-th[3]*dens};
                for (int f=0;f<3;++f) {
                    int l=k+f*n;
                    if (mode==0) p[l]=x[l]-dt*vel[l]+.5*dt*dt*acc[f];
                    else vel[l]=(x[l]-p[l])/dt+.5*dt*acc[f];
                }
            }
        }
        if (drive!=0.) for(int m=0;m<g->ns;++m) {
            int l=g->ind[m]+2*n;
            if(mode==0) p[l]+=.5*dt*dt*drive*g->forma[m];
            else vel[l]+=.5*dt*drive*g->forma[m];
        }
    }
    if(mode==0) return;
    long double total[8]={0};
    for(int i=0;i<g->nr;++i) {
        double erow[8]={0};
        for(int j=0;j<g->nz;++j) {
            int k=(i+1)*s+1+j;
            double dens=a[k]*a[k]+b[k]*b[k], z=c[k], va=vel[k],vb=vel[k+n],vc=vel[k+2*n];
            double H=va*va+vb*vb+.5*vc*vc+th[0]*dens+th[2]*dens*dens+
                     .5*th[1]*z*z+th[3]*z*dens+.5*th[4]*z*z*dens;
            for(int f=0;f<3;++f) {
                const double *u=x+f*n; double u0=u[k];
                double rl=u[k-s]-u0, rr=u[k+s]-u0, zl=u[k-1]-u0,zr=u[k+1]-u0;
                H+=(f==2?.25:.5)*(g->rm[i]*rl*rl+(i==g->nr-1?2.:1.)*g->rp[i]*rr*rr
                   +(j==0?2.:1.)*g->zm[j]*zl*zl+(j==g->nz-1?2.:1.)*g->zp[j]*zr*zr);
            }
            double volume=g->vr[i]*g->vz[j], E=volume*H, Q=2.*volume*(a[k]*vb-b[k]*va);
            int m=i*g->nz+j;double wd=g->wd[m],wr=g->wr[m],we=1.-wd-wr;
            erow[0]+=E; erow[1]+=Q; erow[2]+=wd*E; erow[3]+=wd*Q;
            erow[4]+=wr*E; erow[5]+=wr*Q; erow[6]+=we*E; erow[7]+=we*Q;
        }
        for(int j=0;j<8;++j) total[j]+=erow[j];
    }
    for(int j=0;j<8;++j) res[j]=(double)total[j];
}
