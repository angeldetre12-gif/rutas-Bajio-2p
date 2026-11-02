import csv
from pathlib import Path


def procesar_lote(archivo: str | Path):
    archivo = Path(archivo)
    filas_validas = []
    filas_invalidas = []

    if not archivo.exists():
        return filas_validas, filas_invalidas

    with archivo.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for numero, fila in enumerate(reader, start=2):
            try:
                costo = float(fila.get("costo_base", 0))
                if costo <= 0:
                    raise ValueError("Costo base inválido")
                filas_validas.append(fila)
            except Exception as exc:
                filas_invalidas.append({
                    "linea": numero,
                    "datos": fila,
                    "error": str(exc),
                })

    return filas_validas, filas_invalidas
