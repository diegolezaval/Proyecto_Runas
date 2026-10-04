/* Fused pointwise evaluation of the original M2 potential force.
 * No fast-math, approximation, field elimination or physical change.
 * Projection and radial finite volumes remain in the NumPy implementation.
 */
#include <stddef.h>
void m2_potential_force(size_t n, const double *q, double *out,
                        double mass2, double quartic, double mediator2,
                        double trilinear, double mixed) {
    for (size_t i=0; i<n; ++i) {
        const double a=q[i], b=q[n+i], z=q[2*n+i];
        const double s=a*a+b*b;
        const double fac=mass2+2*quartic*s+trilinear*z+.5*mixed*z*z;
        out[i]=-fac*a;
        out[n+i]=-fac*b;
        out[2*n+i]=-(mediator2+mixed*s)*z-trilinear*s;
    }
}
