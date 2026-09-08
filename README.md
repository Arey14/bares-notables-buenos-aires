# Bares Notables de Buenos Aires — Geolocalización, Rutas Óptimas y Aplicación Web

[![OpenStreetMap](https://img.shields.io/badge/Map-OpenStreetMap-brightgreen.svg)](https://www.openstreetmap.org)
[![Leaflet](https://img.shields.io/badge/UI-Leaflet.js-green.svg)](https://leafletjs.com)
[![Python](https://img.shields.io/badge/Engine-Python%203-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Proyecto integral de análisis geoespacial, optimización de rutas (TSP) y aplicación web interactiva para los **90 Bares Notables de la Ciudad Autónoma de Buenos Aires (CABA)** declarados patrimonio cultural.

---

## Contenido del Proyecto

Este repositorio contiene el flujo completo de datos y visualización:

1. **Geolocalización Catastral:**
   - Normalización de direcciones oficiales mediante el sistema **USIG CABA** (Unidad de Sistemas de Información Geográfica del Gobierno de la Ciudad de Buenos Aires) y verificación con **OpenStreetMap / Nominatim**.
   - Coordenadas exactas (latitud y longitud) de los 90 bares dentro de los límites de CABA.

2. **Cálculo de Recorrido Óptimo (TSP - Traveling Salesperson Problem):**
   - Resolución del problema del viajante mediante heurísticas de optimización combinatoria (*Nearest Neighbor* + *2-Opt Local Search* + *Simulated Annealing*).
   - Recorrido continuo mínimo de **72.18 km** conectando los 90 bares de forma secuencial sin cruces innecesarios.

3. **Planificador Dinámico por Salidas (1 a 30 Viajes):**
   - Algoritmo de partición zonal equilibrada para agrupar los 90 bares según la cantidad de salidas deseadas (desde 3 salidas intensivas de 30 bares hasta 30 paseos tranquilos de 3 bares cada uno).

4. **Aplicación Web Interactiva (`index.html` / `mapa_bares.html`):**
   - Interfaz moderna inspirada en sistemas de diseño *Studio / OpenDesign*.
   - Capas de mapas 100% libres vía OpenStreetMap (sin API Keys ni restricciones).
   - Filtro interactivo por cantidad de salidas (1 a 30 viajes) con paleta dinámica de colores para cada sub-circuito.
   - Búsqueda instantánea de bares y filtro por barrio.
   - Exportación directa de datos en formatos **CSV** y **GeoJSON**.

---

## Estructura del Repositorio

```text
.
├── index.html                   # Aplicación web interactiva (OpenDesign Studio UI)
├── mapa_bares.html              # Copia de la aplicación web para visualización local
├── bares.md                     # Listado original de los 90 Bares Notables
│
├── data/                        # Conjuntos de datos estructurados
│   ├── bares_geolocalizados.csv     # Bares con latitud, longitud y fuente
│   ├── bares_geolocalizados.geojson # Archivo GeoJSON estándar para GIS/Mapas
│   └── recorrido_optimo.csv         # Itinerario secuencial 1-90 con distancias
│
├── docs/                        # Documentación y reportes detallados
│   ├── bares_geolocalizados.md      # Tabla con los 90 bares y enlaces a Google Maps
│   ├── recorrido_optimo.md          # Itinerario del recorrido continuo de 72 km
│   ├── itinerarios_por_viajes.md    # Planes desglosados en 3, 5, 10, 15 y 30 viajes
│   └── guia-de-cafes-notables.pdf   # Guía temática oficial en PDF
│
└── scripts/                     # Scripts de procesamiento y generación
    └── generar_todo.py              # Script en Python para georreferenciar, optimizar y exportar
```

---

## Resumen del Recorrido Óptimo (72.18 km)

El algoritmo organiza el recorrido continuo de forma natural a través de los barrios porteños:

1. **Sudoeste / Oeste:** Mataderos $\rightarrow$ Monte Castro $\rightarrow$ Villa Devoto $\rightarrow$ Villa Santa Rita $\rightarrow$ Flores
2. **Sur:** Nueva Pompeya $\rightarrow$ Boedo $\rightarrow$ San Cristóbal $\rightarrow$ Barracas $\rightarrow$ La Boca
3. **Casco Histórico y Centro:** San Telmo $\rightarrow$ Montserrat $\rightarrow$ Microcentro / San Nicolás $\rightarrow$ Retiro
4. **Norte y Corredor Verde:** Recoleta $\rightarrow$ Once / Balvanera $\rightarrow$ Almagro $\rightarrow$ Caballito $\rightarrow$ Palermo $\rightarrow$ Belgrano $\rightarrow$ Núñez $\rightarrow$ Colegiales $\rightarrow$ Chacarita $\rightarrow$ Villa Urquiza $\rightarrow$ Parque Chas

---

## Ejemplos de Planes por Cantidad de Viajes

| Modalidad | Bares por salida | Distancia prom. por salida | Tipo de experiencia |
|---|:---:|:---:|---|
| **3 Viajes** | ~30 bares | ~24 km | Rutas intensivas en bicicleta o vehículo |
| **5 Viajes** | ~18 bares | ~14 km | Recorridos de día completo por grandes zonas |
| **10 Viajes** | ~9 bares | ~7 km | Salidas de fin de semana por 2 o 3 barrios contiguos |
| **15 Viajes** | ~6 bares | ~4.8 km | Circuitos de tarde |
| **30 Viajes** | 3 bares | ~2.4 km | Mini-paseos a pie para tomar un café y recorrer |

El desglose completo parada por parada se encuentra en [`docs/itinerarios_por_viajes.md`](docs/itinerarios_por_viajes.md).

---

## Cómo usar este proyecto

### 1. Explorar el mapa en tu navegador
Simplemente abre `index.html` (o `mapa_bares.html`) en cualquier navegador web moderno:
- No requiere instalación de librerías ni servidor web local.
- Puedes ajustar el control deslizante para cambiar la cantidad de viajes.
- Puedes aislar cualquier circuito haciendo clic en las píldoras de viaje (`V.1`, `V.2`...).

### 2. Regenerar o personalizar los datos
Si deseas volver a calcular las rutas o modificar los algoritmos, puedes ejecutar el script en Python:

```bash
python3 scripts/generar_todo.py
```

Requisitos: Python 3.8+ (únicamente utiliza la librería estándar: `csv`, `json`, `math`, `urllib`, `re`).

---

## Fuentes de Datos y Créditos

- **Comisión de Protección y Promoción de los Cafés, Bares, Billares y Confiterías Notables de la Ciudad de Buenos Aires** (Ley CABA Nº 35 / Ministerio de Cultura GCBA).
- **USIG (Unidad de Sistemas de Información Geográfica - GCBA):** Servicio de normalización catastral de domicilios de la Ciudad de Buenos Aires.
- **OpenStreetMap & Carto:** Datos cartográficos abiertos y teselas de mapas.
- **Leaflet.js:** Biblioteca open-source para mapas interactivos móviles y de escritorio.

---

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo `LICENSE` para más información.
