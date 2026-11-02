import pytest
import csv

class GestorRutas:
    def __init__(self, archivo_path):
        self.archivo_path = archivo_path
        self.rutas = {}
    def cargar(self):
        if not self.archivo_path.exists(): return
        with open(self.archivo_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.rutas[row["id"]] = row
    def agregar(self, ruta_dict):
        if ruta_dict["id"] in self.rutas:
            raise ValueError("ID duplicado")
        self.rutas[ruta_dict["id"]] = ruta_dict

@pytest.mark.alta
def test_cargar_archivo_inexistente(tmp_path):
    archivo = tmp_path / "no_existe.csv"
    gestor = GestorRutas(archivo)
    gestor.cargar()
    assert gestor.rutas == {}

@pytest.mark.alta
def test_agregar_ruta_duplicada(archivo_csv_temporal, datos_ruta_valida):
    gestor = GestorRutas(archivo_csv_temporal)
    gestor.cargar()
    with pytest.raises(ValueError):
        gestor.agregar(datos_ruta_valida)
