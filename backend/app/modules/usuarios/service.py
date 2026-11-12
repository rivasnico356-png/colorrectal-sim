"""Reglas de negocio de M01: registro con autorizaciones (RF-001, RF-009), sesión y administración de usuarios."""
import json
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errores import ErrorNegocio
from app.core.security import crear_token, hash_contrasena, leer_token, verificar_contrasena
from app.modules.usuarios.schemas import CambioUsuarioIn, CuentaNuevaIn, RegistroIn

VERSION_POLITICA = "1.0"
TIPOS_AUTORIZACION = ("politica_tratamiento", "datos_sensibles", "compartir_avance")

__all__ = ["ErrorNegocio", "registrar", "iniciar_sesion", "cerrar_sesion", "crear_cuenta", "cambiar_usuario", "bitacora"]


def bitacora(db: Session, id_usuario: str, entidad: str, id_entidad: str | None, accion: str, detalle: dict | None = None):
    db.execute(text("""INSERT INTO bitacora_cambios (id_usuario, entidad, id_entidad, accion, detalle)
                       VALUES (CAST(:u AS uuid), :e, :i, :a, CAST(:d AS jsonb))"""),
               {"u": id_usuario, "e": entidad, "i": id_entidad, "a": accion, "d": json.dumps(detalle) if detalle else None})


def _insertar_usuario(db: Session, nombre: str, correo: str, contrasena: str, rango_edad: str, rol: str) -> str:
    if db.execute(text("SELECT 1 FROM usuario WHERE lower(correo) = lower(:c)"), {"c": correo}).first():
        raise ErrorNegocio("Ya existe una cuenta con ese correo.", 409)
    return str(db.execute(
        text("""INSERT INTO usuario (id_rol, id_nivel, nombre, correo, hash_contrasena, rango_edad)
                VALUES ((SELECT id_rol FROM rol WHERE nombre = :r),
                        (SELECT id_nivel FROM nivel ORDER BY puntaje_minimo LIMIT 1), :n, lower(:c), :h, :e)
                RETURNING id_usuario"""),
        {"r": rol, "n": nombre, "c": correo, "h": hash_contrasena(contrasena), "e": rango_edad},
    ).scalar_one())


def registrar(db: Session, datos: RegistroIn) -> str:
    """RF-001 1.1 y RF-009 9.1: toda cuenta creada por registro tiene rol Usuario."""
    id_usuario = _insertar_usuario(db, datos.nombre, datos.correo, datos.contrasena, datos.rango_edad, "Usuario")
    valores = {"politica_tratamiento": True, "datos_sensibles": datos.autoriza_datos_sensibles,
               "compartir_avance": datos.autoriza_compartir}
    for tipo in TIPOS_AUTORIZACION:
        db.execute(
            text("""INSERT INTO autorizacion_datos (id_usuario, tipo, version_politica, aceptada, fecha_aceptacion)
                    VALUES (CAST(:u AS uuid), :t, :v, :a, CASE WHEN :a THEN now() END)"""),
            {"u": id_usuario, "t": tipo, "v": VERSION_POLITICA, "a": valores[tipo]},
        )
    bitacora(db, id_usuario, "usuario", id_usuario, "crear")
    db.commit()
    return id_usuario


def iniciar_sesion(db: Session, correo: str, contrasena: str) -> tuple[str, str]:
    """RF-001 1.2: mensaje genérico y bloqueo temporal tras intentos fallidos."""
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


def cerrar_sesion(db: Session, token: str) -> None:
    """RF-001 1.2b: el token queda invalidado hasta que expire."""
    datos = leer_token(token)
    db.execute(text("""INSERT INTO sesion_revocada (jti, expira) VALUES (CAST(:j AS uuid), to_timestamp(:e))
                       ON CONFLICT (jti) DO NOTHING"""), {"j": datos["jti"], "e": datos["exp"]})
    db.execute(text("DELETE FROM sesion_revocada WHERE expira < now()"))
    db.commit()


def crear_cuenta(db: Session, admin: str, datos: CuentaNuevaIn) -> str:
    """RF-001 1.1: solo el administrador crea cuentas de Profesional de la salud y Administrador."""
    id_usuario = _insertar_usuario(db, datos.nombre, datos.correo, datos.contrasena, datos.rango_edad, datos.rol)
    bitacora(db, admin, "usuario", id_usuario, "crear", {"rol": datos.rol})
    db.commit()
    return id_usuario


def cambiar_usuario(db: Session, admin: str, id_usuario: str, cambio: CambioUsuarioIn) -> None:
    """RF-001 1.5: cambio de rol o estado, registrado en la bitácora."""
    if id_usuario == admin and cambio.estado == "inactivo":
        raise ErrorNegocio("No puedes desactivar tu propia cuenta.", 400)
    actual = db.execute(text("""SELECT r.nombre AS rol, u.estado FROM usuario u JOIN rol r ON r.id_rol = u.id_rol
                                WHERE u.id_usuario = CAST(:u AS uuid) AND u.estado <> 'suprimido'"""),
                        {"u": id_usuario}).mappings().first()
    if actual is None:
        raise ErrorNegocio("Usuario no encontrado.", 404)
    if cambio.rol:
        db.execute(text("UPDATE usuario SET id_rol = (SELECT id_rol FROM rol WHERE nombre = :r) WHERE id_usuario = CAST(:u AS uuid)"),
                   {"r": cambio.rol, "u": id_usuario})
        bitacora(db, admin, "usuario", id_usuario, "cambiar_rol", {"antes": actual["rol"], "despues": cambio.rol})
    if cambio.estado:
        db.execute(text("UPDATE usuario SET estado = :e WHERE id_usuario = CAST(:u AS uuid)"), {"e": cambio.estado, "u": id_usuario})
        bitacora(db, admin, "usuario", id_usuario, "cambiar_estado", {"antes": actual["estado"], "despues": cambio.estado})
    db.commit()
