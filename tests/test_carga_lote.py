import pytest
import csv

def procesar_lote_rutas(archivo_path):
    procesados, errores = [], []
    with open(archivo_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                costo = float(row["costo_base"])
                if costo <= 0: raise ValueError()
                procesados.append(row)
            except Exception as e:
                errores.append({"linea": i, "datos": row, "error": str(e)})
    return procesados, errores

@pytest.mark.media
def test_procesar_lote_con_filas_invalidas(tmp_path):
    archivo = tmp_path / "lote.csv"
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "nombre", "origen", "destino", "costo_base"])
        writer.writerow(["R-001", "R1", "A", "B", "100.0"])
        writer.writerow(["R-002", "R2", "A", "B", "-5.0"])
    p, e = procesar_lote_rutas(archivo)
    assert len(p) == 1 and len(e) == 1
