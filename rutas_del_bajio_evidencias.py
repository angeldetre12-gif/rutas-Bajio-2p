import datetime
import os
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parent


def encabezado(titulo):
    print("=" * 64)
    print("  " + titulo)
    print("  FECHA Y HORA DE EJECUCIÓN:", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "(reloj de Colab)")
    print("=" * 64 + "\n")


def preparar_estructura_pruebas():
    tests_dir = ROOT / "tests"
    tests_dir.mkdir(exist_ok=True)

    (ROOT / "pytest.ini").write_text(
        "[pytest]\nmarkers =\n    alta: Pruebas de prioridad alta\n    media: Pruebas de prioridad media\n    baja: Pruebas de prioridad baja\n",
        encoding="utf-8",
    )

    (tests_dir / "conftest.py").write_text(
        '''import pytest
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
''',
        encoding="utf-8",
    )

    (tests_dir / "test_modelos.py").write_text(
        '''import pytest

class Ruta:
    def __init__(self, id, nombre, origen, destino, costo_base):
        if costo_base <= 0:
            raise ValueError("El costo base debe ser mayor a 0")
        self.id = id
        self.nombre = nombre
        self.origen = origen
        self.destino = destino
        self.costo_base = costo_base

class MaquinaEstadosPedido:
    TRANSICIONES_VALIDAS = {
        "Registrado": ["Validado", "Cancelado"],
        "Validado": ["En tránsito", "Cancelado"],
        "En tránsito": ["Entregado"],
        "Entregado": [],
        "Cancelado": []
    }

    def __init__(self):
        self.estado_actual = "Registrado"

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado in self.TRANSICIONES_VALIDAS.get(self.estado_actual, []):
            self.estado_actual = nuevo_estado
        else:
            raise ValueError("Transición inválida")

@pytest.mark.alta
def test_creacion_ruta_valida(datos_ruta_valida):
    ruta = Ruta(**datos_ruta_valida)
    assert ruta.id == "R-001"

@pytest.mark.media
def test_costo_ruta_invalido():
    with pytest.raises(ValueError):
        Ruta("R-002", "León", "L", "I", -50.0)

@pytest.mark.alta
def test_transicion_estado_valida():
    pedido = MaquinaEstadosPedido()
    pedido.cambiar_estado("Validado")
    assert pedido.estado_actual == "Validado"

@pytest.mark.alta
def test_transicion_estado_invalida():
    pedido = MaquinaEstadosPedido()
    with pytest.raises(ValueError):
        pedido.cambiar_estado("Entregado")
''',
        encoding="utf-8",
    )

    (tests_dir / "test_gestores.py").write_text(
        '''import pytest
import csv

class GestorRutas:
    def __init__(self, archivo_path):
        self.archivo_path = archivo_path
        self.rutas = {}

    def cargar(self):
        if not self.archivo_path.exists():
            return
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
''',
        encoding="utf-8",
    )

    (tests_dir / "test_carga_lote.py").write_text(
        '''import pytest
import csv


def procesar_lote_rutas(archivo_path):
    procesados, errores = [], []
    with open(archivo_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                costo = float(row["costo_base"])
                if costo <= 0:
                    raise ValueError()
                procesados.append(row)
            except Exception:
                errores.append({"linea": i, "datos": row, "error": "valor inválido"})
    return procesados, errores

@pytest.mark.media
def test_procesar_lote_con_filas_invalidas(tmp_path):
    archivo = tmp_path / "lote.csv"
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "nombre", "origen", "destino", "costo_base"])
        writer.writerow(["R-001", "R1", "A", "B", "100.0"])
        writer.writerow(["R-002", "R2", "A", "B", "-5.0"])
    procesados, errores = procesar_lote_rutas(archivo)
    assert len(procesados) == 1 and len(errores) == 1
''',
        encoding="utf-8",
    )


def tarea_2_estructura_pruebas():
    preparar_estructura_pruebas()
    encabezado("TABLA 15: ESTRUCTURA DE LA CARPETA DE PRUEBAS")
    print("Estructura creada en:", ROOT)
    print("\nArchivos generados:")
    for p in sorted(ROOT.glob("**/*.py")) + sorted(ROOT.glob("**/*.ini")):
        print(p.relative_to(ROOT))
    print("\n--- Fixtures en tests/conftest.py ---")
    conftest = (ROOT / "tests/conftest.py").read_text(encoding="utf-8")
    for line in conftest.splitlines():
        if "@pytest.fixture" in line or line.startswith("def "):
            print(line)
    print("\n--- Pruebas por archivo y marcador ---")
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        print(f"[ {path.name} ]")
        for line in text.splitlines():
            if line.startswith("@pytest.mark") or line.startswith("def test_"):
                print(line)
        print()


def ejecutar_paso_3_reporte_final():
    encabezado("FIGURA 7 · TABLA 17: REPORTE FINAL DE PRUEBAS UNITARIAS")
    result = subprocess.run([sys.executable, "-m", "pytest", "-v"], cwd=str(ROOT), capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    print("returncode:", result.returncode)


def ejecutar_marcadores():
    encabezado("FIGURA 8 · TABLA 18: EJECUCIÓN POR MARCADOR ALTA")
    result = subprocess.run([sys.executable, "-m", "pytest", "-v", "-m", "alta"], cwd=str(ROOT), capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

    encabezado("FIGURA 9 · TABLA 18: EJECUCIÓN POR MARCADOR MEDIA")
    result = subprocess.run([sys.executable, "-m", "pytest", "-v", "-m", "media"], cwd=str(ROOT), capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


def ejecutar_lista_cotejo():
    encabezado("FIGURA 10 · TABLA 19: LISTA DE COTEJO")
    subprocess.run([sys.executable, "-m", "pytest", "-q", "--junitxml=resultado.xml"], cwd=str(ROOT), capture_output=True, text=True)
    CRITERIOS = {
        "test_costo_ruta_invalido": ("Ruta (test_modelos.py)", "Validar costo base > 0"),
        "test_creacion_ruta_valida": ("Ruta (test_modelos.py)", "Instanciación correcta con datos válidos"),
        "test_transicion_estado_valida": ("Máquina de estados (test_modelos.py)", "Transición permitida Registrado → Validado"),
        "test_transicion_estado_invalida": ("Máquina de estados (test_modelos.py)", "Bloqueo de la transición Registrado → Entregado"),
        "test_cargar_archivo_inexistente": ("GestorRutas (test_gestores.py)", "Archivo inexistente deja la lista vacía"),
        "test_agregar_ruta_duplicada": ("GestorRutas (test_gestores.py)", "Rechazo de id duplicado"),
        "test_procesar_lote_con_filas_invalidas": ("Procesamiento de lote (test_carga_lote.py)", "Exclusión de filas con costo inválido"),
    }
    filas = []
    tree = ET.parse(ROOT / "resultado.xml")
    for caso in tree.getroot().iter("testcase"):
        nombre = caso.get("name")
        fallo = caso.find("failure") is not None or caso.find("error") is not None
        clase, criterio = CRITERIOS.get(nombre, ("—", "—"))
        filas.append({
            "Clase o módulo": clase,
            "Criterio de aceptación": criterio,
            "Prueba": nombre,
            "Tiempo (s)": round(float(caso.get("time")), 3),
            "Resultado": "FALLÓ" if fallo else "PASÓ",
        })
    for fila in filas:
        print(fila)
    print(f"\nPasaron {(sum(1 for x in filas if x['Resultado'] == 'PASÓ'))} de {len(filas)} pruebas.")


def ejecutar_mutaciones():
    encabezado("FIGURA 12 · TABLAS 18 Y 20: MUTACIONES REALES Y MARCADOR BAJA")
    MUTACIONES = [
        ("MUT-01", "tests/test_modelos.py", "Cambiar '>' por '>=' en la validación de costo_base", "if costo_base <= 0:", "if costo_base < 0:"),
        ("MUT-02", "tests/test_modelos.py", "Permitir Registrado → Entregado", '"Registrado": ["Validado", "Cancelado"]', '"Registrado": ["Validado", "Cancelado", "Entregado"]'),
        ("MUT-03", "tests/test_gestores.py", "Omitir verificación de ID duplicado", 'if ruta_dict["id"] in self.rutas:', "if False:"),
        ("MUT-04", "tests/test_carga_lote.py", "Modificar filtro para aceptar negativos", "if costo <= 0: raise ValueError()", "if costo < -10**9: raise ValueError()"),
    ]

    def correr_pytest():
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=str(ROOT), capture_output=True, text=True)
        ultima = [l for l in r.stdout.splitlines() if l.strip()][-1] if r.stdout.splitlines() else "sin salida"
        return r.returncode, ultima

    codigo, resumen = correr_pytest()
    print("Suite sin mutaciones:", resumen)
    assert codigo == 0

    filas = []
    for ident, archivo, descripcion, original, mutado in MUTACIONES:
        path = ROOT / archivo
        texto = path.read_text(encoding="utf-8")
        if original not in texto:
            filas.append({"ID": ident, "Archivo": archivo, "Modificación": descripcion, "Resultado de pytest": "No aplicada", "Estado": "—"})
            continue
        path.write_text(texto.replace(original, mutado, 1), encoding="utf-8")
        try:
            codigo, resumen = correr_pytest()
        finally:
            path.write_text(texto, encoding="utf-8")
        filas.append({
            "ID": ident,
            "Archivo": archivo,
            "Modificación": descripcion,
            "Resultado de pytest": resumen,
            "Estado": "Detectada" if codigo != 0 else "SOBREVIVIÓ",
        })

    for fila in filas:
        print(fila)
    print(f"\nMutaciones detectadas: {sum(1 for x in filas if x['Estado'] == 'Detectada')} de {len(filas)}")
    print("\n--> Pruebas de prioridad BAJA:")
    result = subprocess.run([sys.executable, "-m", "pytest", "-v", "-m", "baja"], cwd=str(ROOT), capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


def ejecutar_cobertura_criterios():
    encabezado("TABLA 16: COBERTURA DE LA MATRIZ DE CRITERIOS")
    ALTA = {"T-01","T-02","T-03","T-04","T-06","T-08","T-09","T-10","T-12","T-17","T-21","T-23","T-25"}
    PRUEBAS = {
        "T-01": ("test_transicion_estado_valida*", "Parcial"),
        "T-02": ("test_transicion_estado_invalida*", "Parcial"),
        "T-08": ("test_agregar_ruta_duplicada*", "Parcial"),
        "T-21": ("test_cargar_archivo_inexistente*", "Contradice"),
        "T-22": ("test_procesar_lote_con_filas_invalidas*", "Parcial"),
    }
    filas = []
    for i in range(1, 26):
        t = f"T-{i:02d}"
        prueba, res = PRUEBAS.get(t, ("Sin prueba", "—"))
        filas.append({"Criterio": t, "Prioridad": "Alta" if t in ALTA else "Media/Baja", "Prueba": prueba, "Resultado": res})
    for fila in filas:
        print(fila)
    print(f"Criterios: {len(filas)}")
    print(f"Parciales: {sum(1 for x in filas if x['Resultado']=='Parcial')}")


def main():
    print("Iniciando script de evidencias para Rutas del Bajío...")
    tarea_2_estructura_pruebas()
    ejecutar_paso_3_reporte_final()
    ejecutar_marcadores()
    ejecutar_lista_cotejo()
    ejecutar_mutaciones()
    ejecutar_cobertura_criterios()
    print("\nSCRIPT FINALIZADO CORRECTAMENTE.")


if __name__ == "__main__":
    main()
