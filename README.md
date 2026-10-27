# ruteo-casilleros

Prototipo del proyecto de investigación **«Ruteo Dinámico de Vehículos en Escenarios
Logísticos Emergentes — Fase II»** (FPUNE, 2026): ruteo dinámico de vehículos para la carga de
casilleros de comercio electrónico, considerando capacidad de carga, tamaño de la flota y
posición de los vehículos.

- Red vial: OpenStreetMap + OSRM (local).
- Documentación del proyecto, alcance y revisión de la literatura: workspace
  [`proyecto-inv-2026`](https://github.com/SEMP/proyecto-inv-2026).

## Demo: red vial con OSRM

Requisitos: Docker (con Compose) y Python 3 (solo para el demo; no instala nada).

```
docker compose run --rm preparar   # una vez: baja el mapa de Paraguay (~150 MB) y lo procesa
docker compose up -d osrm          # servidor de ruteo en http://localhost:5000
python3 demo/consulta.py           # ruta entre dos puntos y matriz de tiempos entre cinco
docker compose down                # apagar
```

- `preparar` tarda ~1,5 min y deja ~600 MB en `datos/osrm/` (no se versiona). Se corre de nuevo
  solo para actualizar el mapa.
- **Puerto ocupado:** crear un `.env` con `OSRM_PUERTO=5080` (o el que esté libre); el demo lo
  lee también.
- Imagen: `ghcr.io/project-osrm/osrm-backend:v6.0.0`. Las imágenes de Docker Hub
  (`osrm/osrm-backend`) dejaron de actualizarse en 2021.
- Servicios de OSRM que usamos: `route` (ruta entre puntos) y `table` (matriz de tiempos y
  distancias, entrada del ruteo; hasta 1000 × 1000 puntos con la configuración actual).
  Documentación: <https://project-osrm.org/docs/v5.24.0/api/>.

Los puntos del demo son de prueba en Ciudad del Este, no casilleros reales.

Autores: Daisy Kang, Sergio Morel.

Datos de mapas © colaboradores de OpenStreetMap, bajo licencia ODbL.
