// Integra Y'=G Y + (0,F) en un subintervalo. F contiene coeficientes en
// potencias del tiempo local normalizado; no se evalúa una fuerza en el estado Y.
#include <math.h>
#include <string.h>
void march(int n,int degree,int order,double h,double omega,const double *c,
           const double *source,double *x,double *v,double *work,
           double *bound,double *errx,double *errv) {
    int count=3*n;
    double *a=work,*b=a+count,*na=b+count,*nb=na+count,*sum=nb+count;
    memcpy(a,x,count*sizeof(double)); memcpy(b,v,count*sizeof(double));
    for(int j=0;j<count;j++) sum[j]=fabs(x[j]);
    for(int k=0;k<=order;k++) {
        double factor=h/(k+1);
        for(int i=0;i<n;i++){
            int j=3*i;
            const double *s=c+9*i;
            double F[3]={s[2]*a[j]+s[5]*a[j+2]+2*omega*b[j+1],
                         s[3]*a[j+1]-2*omega*b[j],s[4]*a[j+2]+s[6]*a[j]};
            for(int m=0;m<3;m++){
                int l=j+m;
                double left=i?a[l-3]:a[l],right=i+1<n?a[l+3]:0.;
                F[m]+=s[0]*(left-a[l])+s[1]*(right-a[l]);
                if(k<=degree) F[m]+=source[k*count+l];
                na[l]=factor*b[l]; nb[l]=factor*F[m];
                if(k<order){x[l]+=na[l];v[l]+=nb[l];sum[l]+=fabs(na[l]);}
                else{errx[l]=-b[l];errv[l]=-F[m];bound[l]=fmax(bound[l],sum[l]);}
            }
        }
        double *tmp=a;a=na;na=tmp;tmp=b;b=nb;nb=tmp;
    }
}
