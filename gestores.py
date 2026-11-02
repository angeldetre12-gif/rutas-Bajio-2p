import csv
from pathlib import Path


class GestorCSV:
    def __init__(self, archivo: str | Path):
        self.archivo = Path(archivo)

    def cargar(self):
        if not self.archivo.exists():
            return []

        with self.archivo.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def guardar(self, filas):
        fieldnames = list(filas[0].keys()) if filas else []

        with self.archivo.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if fieldnames:
                writer.writeheader()
                writer.writerows(filas)


class GestorRutas(GestorCSV):
    def __init__(self, archivo: str | Path):
        super().__init__(archivo)

    def agregar(self, registro):
        datos = self.cargar()
        if any(r.get("ruta_id") == registro.get("ruta_id") for r in datos):
            raise ValueError("La ruta ya existe.")
        datos.append(registro)
        self.guardar(datos)


class GestorClientes(GestorCSV):
    def __init__(self, archivo: str | Path):
        super().__init__(archivo)

    def agregar(self, registro):
        datos = self.cargar()
        if any(r.get("cliente_id") == registro.get("cliente_id") for r in datos):
            raise ValueError("El cliente ya existe.")
        datos.append(registro)
        self.guardar(datos)


class GestorPedidos(GestorCSV):
    def __init__(self, archivo: str | Path):
        super().__init__(archivo)

    def agregar(self, registro):
        datos = self.cargar()
        if any(r.get("pedido_id") == registro.get("pedido_id") for r in datos):
            raise ValueError("El pedido ya existe.")
        datos.append(registro)
        self.guardar(datos)
