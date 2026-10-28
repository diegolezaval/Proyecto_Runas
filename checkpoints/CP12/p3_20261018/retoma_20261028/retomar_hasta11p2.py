"""Entrada bloqueada: la única repetición9,6→11,2 ya fue ejecutada.

La versión exacta utilizada está conservada en el commit4088598a647401c49b2f944fa08fe8417b45c5a2.
No se importa código científico ni se construye o avanza un integrador.
"""
import json
import sys


def main():
    print(json.dumps({
        "passed": False,
        "blocked": True,
        "reason": "La repetición única9.6→11.2 se consumió. Sus bytes nuevos no están recuperados; otra repetición requiere una excepción explícita adicional y publicación directa verificada.",
        "incident": "INCIDENTE_SEGUNDA_PERDIDA_LOCAL.json",
        "M2_steps_executed": 0,
        "CP12_closed": False
    }, ensure_ascii=False))
    return 3


if __name__ == "__main__":
    sys.exit(main())
