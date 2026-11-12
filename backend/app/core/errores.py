"""Errores de negocio con mensaje para la persona usuaria y código HTTP."""


class ErrorNegocio(Exception):
    def __init__(self, mensaje: str, codigo: int = 400):
        super().__init__(mensaje)
        self.mensaje, self.codigo = mensaje, codigo
