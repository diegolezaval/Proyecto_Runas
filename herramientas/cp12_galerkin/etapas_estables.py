"""Corrección de residuo del mismo sistema de etapas Gauss–Legendre."""
import numpy as np

from fisica import Gauss8


def residual_correction(stepper, u, v):
    """Resolver las etapas por incrementos sin reconstruir su amplitud completa."""
    t = stepper.dt
    predictor = u + t * stepper.c[:, None, None, None] * v
    stage = predictor.copy()
    history = []
    for _ in range(40):
        terms = np.stack([stepper.m2.nonlinear_load(q) - stepper.m2.linear_load(q) for q in stage])
        lhs = np.stack([stepper.m2.mass_load(q) for q in predictor - stage])
        delta = stepper.decompose(lhs + t*t * stepper.combine(stepper.A2, terms))
        next_stage = stage + delta
        scale = stepper.atol + stepper.rtol * np.maximum(abs(next_stage), abs(stage))
        change = float(np.max(abs(next_stage - stage) / scale))
        correction = float(np.max(abs(delta) / scale))
        history.append(dict(incremento=change, correccion=correction))
        stage = next_stage
        if max(change, correction) <= 1.:
            return stage, history
    return None, history


class GaussConCorreccion(Gauss8):
    """Conservar el camino original y corregir sólo el intento que agotó sus etapas."""
    def __init__(self, model, case):
        super().__init__(model, case)
        self.residual_fallback_steps = 0

    def step(self, u, v):
        try:
            return super().step(u, v)
        except ArithmeticError as exc:
            if str(exc) != "Las cuatro etapas Galerkin no convergieron":
                raise
        stages, history = residual_correction(self, u, v)
        if stages is None:
            raise ArithmeticError("La corrección de residuo de etapas tampoco alcanzó la tolerancia")
        self.residual_fallback_steps += 1
        self.max_iterations = max(self.max_iterations, len(history))
        self.max_normalized_change = max(self.max_normalized_change, history[-1]["incremento"])
        accel = np.stack([self.m2.acceleration(q) for q in stages])
        t = self.dt
        return (u + t * v + t*t * self.combine(self.bA[None, :], accel)[0],
                v + t * self.combine(self.b[None, :], accel)[0])


def original_trace(stepper, u, v):
    t = stepper.dt
    c = stepper.c[:, None, None, None]
    base = stepper.m2.mass_load(u) + t*c*stepper.m2.mass_load(v)
    stage = u + t*c*v
    history = []
    for _ in range(24):
        next_stage = stepper.decompose(base + t*t * stepper.combine(
            stepper.A2, np.stack([stepper.m2.nonlinear_load(q) for q in stage])))
        scale = stepper.atol + stepper.rtol * np.maximum(abs(next_stage), abs(stage))
        norm = abs(next_stage-stage) / scale
        i = np.unravel_index(np.argmax(norm), norm.shape)
        change = float(norm[i])
        history.append(dict(change=change, index=list(map(int, i)), abs_delta=float(abs(next_stage[i]-stage[i])),
                            tolerance=float(scale[i])))
        stage = next_stage
        if change <= 1.:
            break
    return history
