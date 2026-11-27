// Operador afín con coeficientes fijos. Campos y velocidades en marco rotante.
#include <math.h>
#include <stddef.h>
static void kick(int n, const double *c, double *x, double *v, double t, double om){
    double co=cos(2*om*t), si=sin(2*om*t);
    double br=si/(2*om), bi=-sin(om*t)*sin(om*t)/om;
    for(int i=0;i<n;i++){
        const double *k=c+9*i;
        int j=3*i;
        double a=x[j],b=x[j+1],z=x[j+2];
        double F[3]={k[2]*a+k[5]*z+k[7],k[3]*b,k[4]*z+k[6]*a+k[8]};
        for(int s=0;s<3;s++){
            double u=x[j+s], left=i?x[j-3+s]:u, right=i+1<n?x[j+3+s]:0.;
            F[s]+=k[0]*(left-u)+k[1]*(right-u);
        }
        double vr=v[j], vi=v[j+1];
        v[j]=co*vr+si*vi+br*F[0]-bi*F[1];
        v[j+1]=-si*vr+co*vi+bi*F[0]+br*F[1];
        v[j+2]+=t*F[2];
    }
}

void advance(int n,int count,double dt,double om,const double *c,double *x,double *v){
    kick(n,c,x,v,.5*dt,om);
    for(int s=0;s<count;s++){
        for(int i=0;i<3*n;i++) x[i]+=dt*v[i];
        kick(n,c,x,v,s+1<count?dt:.5*dt,om);
    }
}
