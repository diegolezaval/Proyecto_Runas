/* Contracción angular de la acción M2 en el subespacio D2 de L=4.
 * T representa el producto de dos armónicos en una base ortonormal.
 * Z representa un armónico simple en esa misma base de productos.
 */
#include <stddef.h>

enum { MODES = 6 };

void m2_angular(size_t nodes, int products, const double *u, const double *t,
                const double *zmap, double lambda, double g, double h,
                double *force, double *potential) {
    for (size_t r = 0; r < nodes; ++r) {
        const double *a = u + r * 3 * MODES;
        const double *b = a + MODES;
        const double *chi = b + MODES;
        double fa[MODES] = {0}, fb[MODES] = {0}, fc[MODES] = {0};
        double energy = 0;
        for (int k = 0; k < products; ++k) {
            const double *matrix = t + k * MODES * MODES;
            const double *zrow = zmap + k * MODES;
            double ax[MODES], bx[MODES], cx[MODES];
            double density = 0, chi2 = 0, chi1 = 0;
            for (int i = 0; i < MODES; ++i) {
                const double *row = matrix + i * MODES;
                double av = 0, bv = 0, cv = 0;
                for (int j = 0; j < MODES; ++j) {
                    av += row[j] * a[j];
                    bv += row[j] * b[j];
                    cv += row[j] * chi[j];
                }
                ax[i] = av;
                bx[i] = bv;
                cx[i] = cv;
                density += a[i] * av + b[i] * bv;
                chi2 += chi[i] * cv;
                chi1 += chi[i] * zrow[i];
            }
            const double phi_factor = 2 * lambda * density + g * chi1 + .5 * h * chi2;
            for (int i = 0; i < MODES; ++i) {
                fa[i] -= phi_factor * ax[i];
                fb[i] -= phi_factor * bx[i];
                fc[i] -= density * (g * zrow[i] + h * cx[i]);
            }
            energy += density * (lambda * density + g * chi1 + .5 * h * chi2);
        }
        for (int i = 0; i < MODES; ++i) {
            force[(r * 3 + 0) * MODES + i] = fa[i];
            force[(r * 3 + 1) * MODES + i] = fb[i];
            force[(r * 3 + 2) * MODES + i] = fc[i];
        }
        potential[r] = energy;
    }
}
