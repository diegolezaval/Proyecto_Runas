/* Referencia/acción del observador. Nunca se conecta al RHS físico de M2. */
#include <stddef.h>
#include <quadmath.h>
void cp12_identity(size_t n, const long double *xi, const long double *xf,
                   long double *difference, long double *residual, double lambda, double g, double h) {
    const __float128 l=lambda, gg=g, hh=h;
    for (size_t i=0;i<n;i++) {
        __float128 ai=xi[i],bi=xi[n+i],zi=xi[2*n+i],af=xf[i],bf=xf[n+i],zf=xf[2*n+i];
        __float128 a=(ai+af)/2,b=(bi+bf)/2,z=(zi+zf)/2,da=ai-af,db=bi-bf,dz=zi-zf;
        __float128 a2=a*a+da*da/12,b2=b*b+db*db/12,z2=z*z+dz*dz/12;
        __float128 fac=2*l*(a2+b2)+gg*z+hh*z2/2;
        __float128 aa=-fac-4*l*a2,bb=-fac-4*l*b2,ab=-4*l*(a*b+da*db/12);
        __float128 az=-gg*a-hh*(z*a+dz*da/12),bz=-gg*b-hh*(z*b+dz*db/12),zz=-hh*(a2+b2);
        __float128 fi=2*l*(ai*ai+bi*bi)+gg*zi+hh*zi*zi/2,ff=2*l*(af*af+bf*bf)+gg*zf+hh*zf*zf/2;
        __float128 exact[3]={-fi*ai+ff*af,-fi*bi+ff*bf,-(gg+hh*zi)*(ai*ai+bi*bi)+(gg+hh*zf)*(af*af+bf*bf)};
        __float128 jac[3]={aa*da+ab*db+az*dz,ab*da+bb*db+bz*dz,2*az*da+2*bz*db+zz*dz};
        for (size_t f=0;f<3;f++) {difference[f*n+i]=(long double)exact[f];residual[f*n+i]=(long double)(jac[f]-exact[f]);}
    }
}
double cp12_quad_epsilon(void) {return (double)FLT128_EPSILON;}
void cp12_jacobian(size_t n, size_t channels, const double *j, const double *x, double *out) {
    for (size_t k=0;k<channels;k++) {
        size_t offset=k*3*n;
        for (size_t i=0;i<n;i++) {
            double a=x[offset+i],b=x[offset+n+i],z=x[offset+2*n+i];
            double aa=j[i],bb=j[n+i],ab=j[2*n+i],az=j[3*n+i],bz=j[4*n+i],zz=j[5*n+i];
            out[offset+i]=aa*a+ab*b+az*z;
            out[offset+n+i]=ab*a+bb*b+bz*z;
            out[offset+2*n+i]=2*az*a+2*bz*b+zz*z;
        }
    }
}
