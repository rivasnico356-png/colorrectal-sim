"""Lee el CSV de estadísticas de Locust y comprueba RNF-001: p90 < 3000 ms y menos de 1 % de errores.

Uso: python pruebas_carga/verificar.py resultados/carga_stats.csv
"""
import csv
import sys

filas = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
total = next(f for f in filas if f["Name"] == "Aggregated")
p90 = float(total["90%"])
peticiones, fallas = int(total["Request Count"]), int(total["Failure Count"])
tasa = 100 * fallas / peticiones if peticiones else 100.0
print(f"Peticiones: {peticiones} · Fallas: {fallas} ({tasa:.2f} %) · p90: {p90:.0f} ms")
for f in filas:
    if f["Name"] != "Aggregated":
        print(f"  {f['Name']}: p90 {f['90%']} ms, {f['Request Count']} peticiones, {f['Failure Count']} fallas")
ok = p90 < 3000 and tasa < 1
print("CUMPLE RNF-001" if ok else "NO CUMPLE RNF-001")
sys.exit(0 if ok else 1)
