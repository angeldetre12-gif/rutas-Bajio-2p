class ErrorDominio(Exception):
    """Base para errores del dominio."""


class RutaInvalidaError(ErrorDominio):
    """Se lanza cuando una ruta no cumple validaciones."""


class ClienteInvalidoError(ErrorDominio):
    """Se lanza cuando un cliente no cumple validaciones."""


class PedidoInvalidoError(ErrorDominio):
    """Se lanza cuando un pedido no cumple validaciones."""
