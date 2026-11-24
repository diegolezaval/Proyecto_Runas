"""Separa en s=0 el inventario de la donante aislada y los términos de superposición en la receptora."""
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from diagnosticar import AQUI, ORIGEN, guardar_json, originales
sys.path.insert(0, str(ORIGEN))
from balances_descarga import observar
from descarga import Malla, compilar, insumos, preparado


def medir():
    campos, _ = insumos(ORIGEN)
    datos = originales()
    salida = {}
    with TemporaryDirectory() as tmp:
        native = compilar(tmp)
        for nombre, h in (("espacial", .40), ("fina", .30)):
            m = Malla(h)
            receptor = datos[nombre]["directa"][0]
            ramas = {}
            for c in ("cargada", "gemelo"):
                donante, _ = preparado(campos[c], m.rd)
                en_receptora = observar(native, m, donante[:3], donante[3:])[4:6]
                del donante
                montado = datos[nombre][c][0]
                medidas = {}
                for k, aislada in zip(("E_r","Q_r"), en_receptora):
                    exceso = float(montado[k] - receptor[k])
                    medidas[k] = dict(exceso_sobre_receptora_aislada=exceso,
                                      donante_aislada_en_receptora=float(aislada),
                                      termino_de_superposicion=exceso-float(aislada))
                ramas[c] = medidas
            diferencias = {}
            for k in ("E_r", "Q_r"):
                dif = {a:ramas["cargada"][k][a]-ramas["gemelo"][k][a] for a in ramas["cargada"][k]}
                dif["fraccion_donante_aislada"] = dif["donante_aislada_en_receptora"]/dif["exceso_sobre_receptora_aislada"]
                diferencias[k] = dif
            salida[str(h)] = dict(aisladas_y_superposiciones=ramas,cargada_menos_gemela=diferencias)
    return dict(unidades="M2 normalizadas",s=0,radio_nucleo=40,
                metodo="El montaje directo en s=0 es la receptora aislada. Se mide además, sin evolución, la donante aislada a distancia 120 en el mismo volumen receptor.",
                mapeos=salida)


if __name__ == "__main__":
    guardar_json(AQUI/"SOLAPAMIENTO_INICIAL.json", medir())
