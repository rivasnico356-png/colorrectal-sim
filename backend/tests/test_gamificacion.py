"""RF-006: puntaje, nivel e insignias.

Las primeras pruebas son unitarias puras: evalúan las reglas de insignias con una base de datos simulada.
La última (CP042) comprueba el cambio de nivel contra PostgreSQL.
"""
from sqlalchemy import text

from app import preparar
from app.core.db import SessionLocal
from app.core.eventos import DecisionRegistrada
from app.modules.gamificacion.service import _cumple, al_registrar_decision
from tests.conftest import correo, requiere_db


class _Resultado:
    def __init__(self, valor):
        self.valor = valor

    def scalar(self):
        return self.valor


class _BaseSimulada:
    """Devuelve el valor indicado en cada consulta y cuenta cuántas consultas recibió."""

    def __init__(self, valor):
        self.valor, self.consultas = valor, 0

    def execute(self, *_args, **_kwargs):
        self.consultas += 1
        return _Resultado(self.valor)


def _evento(finalizado: bool = False) -> DecisionRegistrada:
    return DecisionRegistrada(db=None, id_usuario="u", id_intento=1, id_etapa=1, es_correcta=True, siguio_ia=False,
                              ia_erronea=False, puntaje=100, intento_finalizado=finalizado)


def test_insignia_por_casos_completados_respeta_el_minimo():
    assert _cumple(_BaseSimulada(3), "u", "casos_completados>=3", _evento()) is True
    assert _cumple(_BaseSimulada(2), "u", "casos_completados>=3", _evento()) is False


def test_caso_perfecto_solo_al_terminar_el_intento_y_sin_errores():
    sin_terminar = _BaseSimulada(0)
    assert _cumple(sin_terminar, "u", "caso_perfecto", _evento(finalizado=False)) is False
    assert sin_terminar.consultas == 0
    assert _cumple(_BaseSimulada(0), "u", "caso_perfecto", _evento(finalizado=True)) is True
    assert _cumple(_BaseSimulada(1), "u", "caso_perfecto", _evento(finalizado=True)) is False


def test_insignia_por_detectar_la_ia_equivocada():
    assert _cumple(_BaseSimulada(1), "u", "ia_erronea_detectada>=1", _evento()) is True
    assert _cumple(_BaseSimulada(0), "u", "ia_erronea_detectada>=1", _evento()) is False


def test_regla_desconocida_no_otorga_insignia():
    assert _cumple(_BaseSimulada(99), "u", "regla_inventada", _evento()) is False


@requiere_db
def test_cambio_de_nivel_al_superar_el_puntaje_minimo():
    """CP042 (RF-006 6.1): con 490 puntos sigue en Explorador; al sumar 20 pasa a Analista (500) y lo informa una vez."""
    preparar.aplicar_esquema()
    with SessionLocal() as db:
        u = preparar._crear_usuario(db, "Usuario", "Prueba de nivel", correo("nivel"), "Segura123")
        db.execute(text("""UPDATE usuario SET puntaje_acumulado = 490,
                                  id_nivel = (SELECT id_nivel FROM nivel WHERE nombre = 'Explorador')
                           WHERE id_usuario = CAST(:u AS uuid)"""), {"u": u})
        db.commit()

        def evento(puntos: int) -> DecisionRegistrada:
            return DecisionRegistrada(db=db, id_usuario=u, id_intento=0, id_etapa=0, es_correcta=True, siguio_ia=False,
                                      ia_erronea=False, puntaje=puntos)

        assert al_registrar_decision(evento(5))["nivel_nuevo"] is None
        assert al_registrar_decision(evento(20))["nivel_nuevo"] == "Analista"
        assert al_registrar_decision(evento(10))["nivel_nuevo"] is None
        fila = db.execute(text("""SELECT u.puntaje_acumulado, n.nombre FROM usuario u JOIN nivel n ON n.id_nivel = u.id_nivel
                                  WHERE u.id_usuario = CAST(:u AS uuid)"""), {"u": u}).one()
        db.rollback()
    assert (fila.puntaje_acumulado, fila.nombre) == (525, "Analista")
