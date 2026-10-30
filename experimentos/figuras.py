"""Figuras y resumen agregado del experimento línea recta vs red vial.

Lee los `*_detalle.json` que deja `linea_recta_vs_red.py` (una corrida por semilla) y
genera, sin dependencias externas:

- `figuras/circuidad_fda.svg`: función de distribución acumulada de la circuidad por ciudad.
- `figuras/exceso_fda.svg`: ídem del exceso de tiempo de las rutas planificadas en línea recta.
- `agregado.json`: métricas con todas las semillas juntas.

    python3 experimentos/figuras.py experimentos/resultados
"""

import glob
import json
import os
import statistics
import sys

COLORES = {"Asunción": "#1b6f8a", "Ciudad del Este": "#c0612b"}
ORDEN = ["Asunción", "Ciudad del Este"]


def percentil(valores, p):
    valores = sorted(valores)
    return valores[min(len(valores) - 1, int(round(p / 100 * (len(valores) - 1))))]


def fda_svg(series, titulo_x, x_min, x_max, ticks_x, formato_x, ruta):
    """Gráfico de líneas escalonadas: una FDA empírica por serie."""
    ancho, alto = 640, 400
    izq, der, arr, aba = 64, 24, 20, 56
    w, h = ancho - izq - der, alto - arr - aba

    def px(x):
        return izq + (min(max(x, x_min), x_max) - x_min) / (x_max - x_min) * w

    def py(y):
        return arr + (1 - y) * h

    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" '
              f'font-family="Helvetica, Arial, sans-serif" font-size="13">',
              f'<rect width="{ancho}" height="{alto}" fill="#ffffff"/>']
    for y in [0, 0.25, 0.5, 0.75, 1]:
        partes.append(f'<line x1="{izq}" y1="{py(y):.1f}" x2="{izq + w}" y2="{py(y):.1f}" stroke="#e3e3e3"/>')
        etiqueta = f"{y:.2f}".replace(".", ",")
        partes.append(f'<text x="{izq - 8}" y="{py(y) + 4:.1f}" text-anchor="end" fill="#333">{etiqueta}</text>')
    for x in ticks_x:
        partes.append(f'<line x1="{px(x):.1f}" y1="{arr}" x2="{px(x):.1f}" y2="{arr + h}" stroke="#eeeeee"/>')
        partes.append(f'<text x="{px(x):.1f}" y="{arr + h + 18}" text-anchor="middle" fill="#333">{formato_x(x)}</text>')
    partes.append(f'<rect x="{izq}" y="{arr}" width="{w}" height="{h}" fill="none" stroke="#888"/>')
    partes.append(f'<text x="{izq + w / 2}" y="{alto - 12}" text-anchor="middle" fill="#111">{titulo_x}</text>')
    partes.append(f'<text transform="translate(16 {arr + h / 2}) rotate(-90)" text-anchor="middle" fill="#111">Proporción acumulada</text>')

    for k, nombre in enumerate(ORDEN):
        valores = sorted(series[nombre])
        if len(valores) > 500:  # con decenas de miles de pares, 500 cuantiles alcanzan a la vista
            valores = [valores[round(q * (len(valores) - 1) / 499)] for q in range(500)]
        n = len(valores)
        puntos = [f"{px(x_min):.1f},{py(0):.1f}"]
        for i, v in enumerate(valores):
            puntos.append(f"{px(v):.1f},{py(i / n):.1f}")
            puntos.append(f"{px(v):.1f},{py((i + 1) / n):.1f}")
        puntos.append(f"{px(x_max):.1f},{py(1):.1f}")
        partes.append(f'<polyline points="{" ".join(puntos)}" fill="none" stroke="{COLORES[nombre]}" stroke-width="2"/>')
        ly = arr + h - 44 + k * 20
        partes.append(f'<line x1="{izq + w - 150}" y1="{ly}" x2="{izq + w - 126}" y2="{ly}" stroke="{COLORES[nombre]}" stroke-width="3"/>')
        partes.append(f'<text x="{izq + w - 120}" y="{ly + 4}" fill="#111">{nombre}</text>')
    partes.append("</svg>")
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(partes))


def main():
    carpeta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "resultados")
    archivos = sorted(glob.glob(os.path.join(carpeta, "linea_recta_vs_red*_detalle.json")))
    circuidad = {n: [] for n in ORDEN}
    excesos = {n: [] for n in ORDEN}
    for ruta in archivos:
        for detalle in json.load(open(ruta, encoding="utf-8")):
            circuidad[detalle["ciudad"]] += [d / r for r, d, _ in detalle["pares_recta_dist_tiempo"]]
            excesos[detalle["ciudad"]] += detalle["excesos_pct"]

    agregado = {"corridas": len(archivos), "ciudades": []}
    for n in ORDEN:
        c, e = circuidad[n], excesos[n]
        agregado["ciudades"].append({
            "ciudad": n, "pares": len(c), "instancias": len(e),
            "circuidad_mediana": statistics.median(c), "circuidad_p10": percentil(c, 10),
            "circuidad_p90": percentil(c, 90),
            "exceso_mediana_pct": statistics.median(e), "exceso_media_pct": statistics.mean(e),
            "exceso_p90_pct": percentil(e, 90), "exceso_max_pct": max(e),
            "instancias_con_exceso_pct": 100 * sum(x > 0.01 for x in e) / len(e),
        })
    with open(os.path.join(carpeta, "agregado.json"), "w", encoding="utf-8") as archivo:
        json.dump(agregado, archivo, ensure_ascii=False, indent=2)
    print(json.dumps(agregado, ensure_ascii=False, indent=2))

    figuras = os.path.join(carpeta, "figuras")
    os.makedirs(figuras, exist_ok=True)
    fda_svg(circuidad, "Índice de circuidad (distancia por carretera / distancia euclidiana)",
            1.0, 2.5, [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5], lambda x: f"{x:.2f}".replace(".", ","),
            os.path.join(figuras, "circuidad_fda.svg"))
    fda_svg(excesos, "Exceso de tiempo de la ruta planificada con distancia euclidiana (%)",
            -12, 21, [-10, -5, 0, 5, 10, 15, 20], lambda x: f"{x:g}".replace("-", "−"), os.path.join(figuras, "exceso_fda.svg"))


if __name__ == "__main__":
    main()
