import pytest

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
            raise ValueError(f"Transición inválida")

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
