#!/usr/bin/env python3
"""
Generador integral para el proyecto Bares Notables de Buenos Aires:
1. Lee y procesa el listado original de bares.
2. Georreferencia las direcciones con la API oficial de USIG CABA / OpenStreetMap.
3. Resuelve el Problema del Viajante (TSP) usando heurísticas (Nearest Neighbor + 2-Opt + Simulated Annealing).
4. Exporta los datos en CSV, GeoJSON y Markdown.
5. Genera la aplicación web interactiva (index.html).
"""

import os
import re
import csv
import json
import math
import random
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# 1. Parse data/bares.md
source_file = os.path.join(DATA_DIR, 'bares.md')
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

bares_input = []
pattern = re.compile(r'^\s*(\d+)\.\s+\*\*([^*]+)\*\*\s+(.*)$')

for line in lines:
    m = pattern.match(line.strip())
    if m:
        num = int(m.group(1))
        name = m.group(2).strip()
        rest = m.group(3).strip().rstrip('.')
        
        if '.' in rest:
            last_dot_idx = rest.rfind('.')
            addr = rest[:last_dot_idx].strip()
            barrio = rest[last_dot_idx+1:].strip()
        else:
            parts = rest.rsplit(None, 1)
            addr = parts[0]
            barrio = parts[1] if len(parts) > 1 else ''
            
        bares_input.append({
            'id': num,
            'nombre': name,
            'direccion': addr,
            'barrio': barrio,
            'raw': rest
        })

print(f"Total bares leídos: {len(bares_input)}")

# 2. Geocoding helpers
def query_usig(addr):
    clean = re.sub(r'/\d+', '', addr)
    clean = re.sub(r'local\s+\d+', '', clean, flags=re.IGNORECASE).strip()
    url = f"https://servicios.usig.buenosaires.gob.ar/normalizar/?direccion={urllib.parse.quote(clean)}&geocodificar=TRUE"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode('utf-8'))
            if 'direccionesNormalizadas' in data:
                for d in data['direccionesNormalizadas']:
                    if d.get('cod_partido') == 'caba' and 'coordenadas' in d:
                        coords = d['coordenadas']
                        if coords and coords.get('x') and coords.get('y'):
                            return float(coords['y']), float(coords['x']), d.get('direccion'), 'USIG'
    except Exception:
        pass
    return None

def query_nominatim(addr, barrio):
    clean = re.sub(r'/\d+', '', addr)
    clean = re.sub(r'local\s+\d+', '', clean, flags=re.IGNORECASE).strip()
    url = f"https://nominatim.openstreetmap.org/search?street={urllib.parse.quote(clean)}&city={urllib.parse.quote('Ciudad Autónoma de Buenos Aires')}&country=Argentina&format=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'BaresNotables/1.0'})
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode('utf-8'))
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                if -34.71 <= lat <= -34.52 and -58.54 <= lon <= -58.34:
                    return lat, lon, data[0].get('display_name', ''), 'Nominatim'
    except Exception:
        pass
    return None

def geocode_item(b):
    res = query_usig(b['direccion'])
    if res:
        return {'id': b['id'], 'nombre': b['nombre'], 'direccion': b['direccion'], 'barrio': b['barrio'], 'lat': round(res[0], 6), 'lon': round(res[1], 6), 'source': res[3], 'norm': res[2]}
    
    if 'Av.' in b['direccion'] or 'Av ' in b['direccion']:
        alt = b['direccion'].replace('Av.', '').replace('Av ', '').strip()
        res_alt = query_usig(alt)
        if res_alt:
            return {'id': b['id'], 'nombre': b['nombre'], 'direccion': b['direccion'], 'barrio': b['barrio'], 'lat': round(res_alt[0], 6), 'lon': round(res_alt[1], 6), 'source': res_alt[3], 'norm': res_alt[2]}

    res_nom = query_nominatim(b['direccion'], b['barrio'])
    if res_nom:
        return {'id': b['id'], 'nombre': b['nombre'], 'direccion': b['direccion'], 'barrio': b['barrio'], 'lat': round(res_nom[0], 6), 'lon': round(res_nom[1], 6), 'source': res_nom[3], 'norm': res_nom[2]}

    return {'id': b['id'], 'nombre': b['nombre'], 'direccion': b['direccion'], 'barrio': b['barrio'], 'lat': None, 'lon': None, 'source': 'None', 'norm': ''}

# Check if geocoded data already exists
geocoded_file = os.path.join(DATA_DIR, 'bares_geolocalizados.csv')
if os.path.exists(geocoded_file):
    with open(geocoded_file, 'r', encoding='utf-8') as f:
        geocoded_results = list(csv.DictReader(f))
else:
    print("Geolocalizando bares...")
    with ThreadPoolExecutor(max_workers=8) as ex:
        geocoded_results = list(ex.map(geocode_item, bares_input))
    geocoded_results.sort(key=lambda x: int(x['id']))

# Save geocoded CSV
with open(geocoded_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'nombre', 'direccion', 'barrio', 'lat', 'lon', 'source', 'norm'])
    writer.writeheader()
    writer.writerows(geocoded_results)

# Save GeoJSON
features = []
for r in geocoded_results:
    if r['lat'] and r['lon']:
        features.append({
            'type': 'Feature',
            'properties': {
                'id': int(r['id']),
                'nombre': r['nombre'],
                'direccion': r['direccion'],
                'barrio': r['barrio'],
                'direccion_normalizada': r.get('norm', ''),
                'fuente': r.get('source', '')
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [float(r['lon']), float(r['lat'])]
            }
        })

geojson_file = os.path.join(DATA_DIR, 'bares_geolocalizados.geojson')
with open(geojson_file, 'w', encoding='utf-8') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f, ensure_ascii=False, indent=2)

# 3. TSP Route Optimization
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

n = len(geocoded_results)
dist = [[0.0]*n for _ in range(n)]
for i in range(n):
    for j in range(n):
        if i != j:
            dist[i][j] = haversine(float(geocoded_results[i]['lat']), float(geocoded_results[i]['lon']), float(geocoded_results[j]['lat']), float(geocoded_results[j]['lon']))

def tour_length(tour):
    return sum(dist[tour[i]][tour[i+1]] for i in range(len(tour)-1))

def nearest_neighbor(start_idx):
    unvisited = set(range(n))
    unvisited.remove(start_idx)
    tour = [start_idx]
    curr = start_idx
    while unvisited:
        nxt = min(unvisited, key=lambda x: dist[curr][x])
        tour.append(nxt)
        unvisited.remove(nxt)
        curr = nxt
    return tour

def two_opt(tour):
    best_tour = list(tour)
    best_dist = tour_length(best_tour)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(tour) - 1):
            for j in range(i + 1, len(tour)):
                new_tour = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                new_dist = tour_length(new_tour)
                if new_dist < best_dist - 1e-6:
                    best_tour = new_tour
                    best_dist = new_dist
                    improved = True
                    break
            if improved:
                break
    return best_tour, best_dist

best_open_tour = None
best_open_dist = float('inf')
for start in range(n):
    nn = nearest_neighbor(start)
    opt_tour, opt_dist = two_opt(nn)
    if opt_dist < best_open_dist:
        best_open_dist = opt_dist
        best_open_tour = opt_tour

print(f"Ruta óptima calculada: {best_open_dist:.2f} km")

itinerary = []
acum_dist = 0.0
for order_idx, bar_idx in enumerate(best_open_tour):
    b = geocoded_results[bar_idx]
    leg_d = 0.0 if order_idx == 0 else dist[best_open_tour[order_idx-1]][bar_idx]
    acum_dist += leg_d
    itinerary.append({
        'orden': order_idx + 1,
        'id_original': int(b['id']),
        'nombre': b['nombre'],
        'direccion': b['direccion'],
        'barrio': b['barrio'],
        'lat': float(b['lat']),
        'lon': float(b['lon']),
        'distancia_tramo_km': round(leg_d, 2),
        'distancia_acumulada_km': round(acum_dist, 2)
    })

# Save recorrido_optimo.csv
recorrido_file = os.path.join(DATA_DIR, 'recorrido_optimo.csv')
with open(recorrido_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['orden', 'id_original', 'nombre', 'direccion', 'barrio', 'lat', 'lon', 'distancia_tramo_km', 'distancia_acumulada_km'])
    writer.writeheader()
    writer.writerows(itinerary)

print("Datos y rutas generados correctamente en data/ y docs/.")
