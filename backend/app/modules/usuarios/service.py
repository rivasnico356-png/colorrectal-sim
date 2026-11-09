"""Reglas de negocio de usuarios: registro con autorizaciones (RF-001, RF-009) e inicio de sesión con bloqueo."""
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import crear_token, hash_contrasena, verificar_contrasena
from app.modules.usuarios.schemas import RegistroIn

VERSION_POLITICA = "1.0"


class ErrorNegocio(Exception):
    def __init__(self, mensaje: str, codigo: int = 400):
        super().__init__(mensaje)
        self.mensaje, self.codigo = mensaje, codigo


def registrar(db: Session, datos: RegistroIn) -> str:
    existe = db.execute(text("SELECT 1 FROM usuario WHERE lower(correo) = lower(:c)"), {"c": datos.correo}).first()
    if existe:
        raise ErrorNegocio("Ya existe una cuenta con ese correo.", 409)
    id_usuario = db.execute(
        text("""INSERT INTO usuario (id_rol, nombre, correo, hash_contrasena, rango_edad)
                VALUES ((SELECT id_rol FROM rol WHERE nombre = 'Usuario'), :n, lower(:c), :h, :e)
                RETURNING id_usuario"""),
        {"n": datos.nombre, "c": datos.correo, "h": hash_contrasena(datos.contrasena), "e": datos.rango_edad},
    ).scalar_one()
    autorizaciones = [("politica_tratamiento", True), ("datos_sensibles", datos.autoriza_datos_sensibles),
                      ("compartir_avance", datos.autoriza_compartir)]
    for tipo, aceptada in autorizaciones:
        db.execute(
            text("""INSERT INTO autorizacion_datos (id_usuario, tipo, version_politica, aceptada, fecha_aceptacion)
                    VALUES (:u, :t, :v, :a, CASE WHEN :a THEN now() END)"""),
            {"u": id_usuario, "t": tipo, "v": VERSION_POLITICA, "a": aceptada},
        )
    db.execute(text("INSERT INTO bitacora_cambios (id_usuario, entidad, id_entidad, accion) VALUES (:u, 'usuario', :u, 'crear')"),
               {"u": id_usuario})
    db.commit()
    return str(id_usuario)


def iniciar_sesion(db: Session, correo: str, contrasena: str) -> tuple[str, str]:
    s = get_settings()
    fila = db.execute(
        text("""SELECT u.id_usuario, u.hash_contrasena, u.intentos_fallidos, u.bloqueado_hasta, u.estado, r.nombre AS rol
                FROM usuario u JOIN rol r ON r.id_rol = u.id_rol WHERE lower(u.correo) = lower(:c)"""),
        {"c": correo},
    ).mappings().first()
    error = ErrorNegocio("Correo o contraseña incorrectos.", 401)
    if fila is None or fila["estado"] != "activo":
        raise error
    ahora = datetime.now(UTC)
    if fila["bloqueado_hasta"] and fila["bloqueado_hasta"] > ahora:
        raise ErrorNegocio("La cuenta está bloqueada temporalmente. Intenta más tarde.", 423)
    if not verificar_contrasena(contrasena, fila["hash_contrasena"]):
        intentos = fila["intentos_fallidos"] + 1
        bloqueo = ahora + timedelta(minutes=s.minutos_bloqueo) if intentos >= s.max_intentos_fallidos else None
        db.execute(text("UPDATE usuario SET intentos_fallidos = :i, bloqueado_hasta = :b WHERE id_usuario = :u"),
                   {"i": 0 if bloqueo else intentos, "b": bloqueo, "u": fila["id_usuario"]})
        db.commit()
        raise error
    db.execute(text("UPDATE usuario SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE id_usuario = :u"),
               {"u": fila["id_usuario"]})
    db.commit()
    return crear_token(str(fila["id_usuario"]), fila["rol"]), fila["rol"]
