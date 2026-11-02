from dataclasses import dataclass
from typing import Optional


@dataclass
class Cliente:
    cliente_id: str
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None


@dataclass
class Ruta:
    ruta_id: str
    origen: str
    destino: str
    costo_base: float

    def __post_init__(self):
        if self.costo_base <= 0:
            raise ValueError("El costo base debe ser mayor que cero.")


@dataclass
class Pedido:
    pedido_id: str
    cliente_id: str
    ruta_id: str
    cantidad: int = 1
    estado: str = "registrado"

    def __post_init__(self):
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
