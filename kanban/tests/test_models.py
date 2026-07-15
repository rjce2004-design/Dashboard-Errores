import pytest
from kanban.models import Defecto, PruebaUnitaria, Sprint


@pytest.mark.django_db
class TestFlujoDeEstados:

    def test_defecto_nuevo_inicia_en_abierto(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", severidad="MEDIA")
        assert bug.estado == "ABIERTO"

    def test_siguiente_estado_avanza_en_orden(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="ABIERTO")
        etiqueta, codigo = bug.siguiente_estado()
        assert codigo == "ANALISIS"

    def test_siguiente_estado_desde_cerrado_es_none(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="CERRADO")
        assert bug.siguiente_estado() is None

    def test_anterior_estado_retrocede_en_orden(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="RESUELTO")
        etiqueta, codigo = bug.anterior_estado()
        assert codigo == "CORRECCION"

    def test_anterior_estado_desde_abierto_es_none(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="ABIERTO")
        assert bug.anterior_estado() is None

    def test_defecto_cerrado_no_avanza_ni_retrocede(self):
        """Un defecto Cerrado no se puede modificar en ninguna dirección."""
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="CERRADO")
        assert bug.siguiente_estado() is None
        assert bug.anterior_estado() is None


@pytest.mark.django_db
class TestReglaPruebasUnitarias:
    """Requisito 6: no se puede pasar a RESUELTO sin al menos una prueba registrada."""

    def test_no_puede_resolverse_sin_pruebas(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="CORRECCION")
        assert bug.puede_pasar_a_resuelto() is False

    def test_puede_resolverse_con_al_menos_una_prueba(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="CORRECCION")
        PruebaUnitaria.objects.create(defecto=bug, nombre_prueba="test_login", resultado="PASO")
        assert bug.puede_pasar_a_resuelto() is True

    def test_prueba_fallida_tambien_cuenta_como_registrada(self):
        """La regla es 'al menos una prueba registrada', no 'al menos una prueba exitosa'."""
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="CORRECCION")
        PruebaUnitaria.objects.create(defecto=bug, nombre_prueba="test_login", resultado="FALLO")
        assert bug.puede_pasar_a_resuelto() is True


@pytest.mark.django_db
class TestReglaSprints:
    """No se puede asignar una tarea a un sprint ya cerrado."""

    def test_puede_asignarse_a_sprint_abierto(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc")
        sprint = Sprint.objects.create(
            nombre="Sprint 1", fecha_inicio="2026-01-01", fecha_fin="2026-01-15", estado="ABIERTO"
        )
        assert bug.puede_asignarse_a_sprint(sprint) is True

    def test_no_puede_asignarse_a_sprint_cerrado(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc")
        sprint = Sprint.objects.create(
            nombre="Sprint 1", fecha_inicio="2026-01-01", fecha_fin="2026-01-15", estado="CERRADO"
        )
        assert bug.puede_asignarse_a_sprint(sprint) is False

    def test_quitar_sprint_siempre_es_valido(self):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc")
        assert bug.puede_asignarse_a_sprint(None) is True