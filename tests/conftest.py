import pytest
import csv

@pytest.fixture
def datos_ruta_valida():
    return {"id": "R-001", "nombre": "León - Silao", "origen": "León", "destino": "Silao", "costo_base": 150.0}

@pytest.fixture
def archivo_csv_temporal(tmp_path):
    archivo = tmp_path / "rutas_prueba.csv"
    with open(archivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "nombre", "origen", "destino", "costo_base"])
        writer.writerow(["R-001", "León - Silao", "León", "Silao", "150.0"])
    return archivo
