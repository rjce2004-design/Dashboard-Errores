"""
Pruebas de integración sobre las vistas de kanban/views.py.

Cubren:
- Avanzar y retroceder de estado vía HTTP
- Que el historial y las notificaciones se generen (Requisitos 8 y 9)
- Que borrar una HU o un Equipo NO borre los defectos asociados
- Bloqueo de avance a RESUELTO sin pruebas
"""
import pytest
from django.urls import reverse
from kanban.models import (
    Defecto, HistoriaUsuario, Equipo, PruebaUnitaria,
    HistorialEstado, Notificacion,
)


@pytest.mark.django_db
class TestAvanzarYRetrocederEstado:

    def test_avanzar_estado_mueve_el_defecto(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="ABIERTO")
        client.post(reverse('avanzar_estado', args=[bug.id]), {'responsable': 'Ana'})
        bug.refresh_from_db()
        assert bug.estado == "ANALISIS"

    def test_avanzar_a_resuelto_sin_pruebas_es_bloqueado(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="CORRECCION")
        client.post(reverse('avanzar_estado', args=[bug.id]), {'responsable': 'Ana'})
        bug.refresh_from_db()
        assert bug.estado == "CORRECCION"  # no avanzó

    def test_avanzar_a_resuelto_con_prueba_si_funciona(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="CORRECCION")
        PruebaUnitaria.objects.create(defecto=bug, nombre_prueba="t1", resultado="PASO")
        client.post(reverse('avanzar_estado', args=[bug.id]), {'responsable': 'Ana'})
        bug.refresh_from_db()
        assert bug.estado == "RESUELTO"

    def test_retroceder_estado_mueve_el_defecto_hacia_atras(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="ANALISIS")
        client.post(reverse('retroceder_estado', args=[bug.id]), {'responsable': 'Ana'})
        bug.refresh_from_db()
        assert bug.estado == "ABIERTO"

    def test_defecto_cerrado_ignora_intentos_de_avanzar_o_retroceder(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="CERRADO")
        client.post(reverse('avanzar_estado', args=[bug.id]), {'responsable': 'Ana'})
        client.post(reverse('retroceder_estado', args=[bug.id]), {'responsable': 'Ana'})
        bug.refresh_from_db()
        assert bug.estado == "CERRADO"


@pytest.mark.django_db
class TestHistorialYNotificaciones:
    """Requisitos 8 y 9."""

    def test_avanzar_estado_crea_registro_de_historial_con_responsable(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="ABIERTO")
        client.post(reverse('avanzar_estado', args=[bug.id]), {'responsable': 'Carlos'})

        historial = HistorialEstado.objects.filter(defecto=bug).first()
        assert historial is not None
        assert historial.estado_anterior == "ABIERTO"
        assert historial.estado_nuevo == "ANALISIS"
        assert historial.responsable == "Carlos"

    def test_avanzar_estado_crea_notificacion(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="ABIERTO")
        client.post(reverse('avanzar_estado', args=[bug.id]), {'responsable': 'Carlos'})
        assert Notificacion.objects.filter(defecto=bug).exists()

    def test_sin_responsable_se_usa_valor_por_defecto(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", estado="ABIERTO")
        client.post(reverse('avanzar_estado', args=[bug.id]), {})
        historial = HistorialEstado.objects.filter(defecto=bug).first()
        assert historial.responsable == "Sin especificar"

    def test_asignar_equipo_crea_notificacion(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc")
        equipo = Equipo.objects.create(nombre_equipo="Equipo A", lider="Juan")
        client.post(
            reverse('asignar_equipo', args=[bug.id]),
            {'equipo_id': equipo.id, 'desarrollador_id': '', 'responsable': 'Ana'},
        )
        assert Notificacion.objects.filter(defecto=bug).exists()

    def test_asignar_equipo_sin_cambios_no_duplica_notificacion(self, client):
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc")
        client.post(
            reverse('asignar_equipo', args=[bug.id]),
            {'equipo_id': '', 'desarrollador_id': '', 'responsable': 'Ana'},
        )
        assert Notificacion.objects.filter(defecto=bug).count() == 0


@pytest.mark.django_db
class TestEliminacionSegura:
    """Borrar una HU o un Equipo no debe borrar los defectos asociados."""

    def test_eliminar_hu_no_borra_el_defecto(self, client):
        hu = HistoriaUsuario.objects.create(codigo_hu="HU01", descripcion_hu="desc")
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", historia_usuario=hu)

        client.post(reverse('eliminar_hu', args=[hu.id]))

        bug.refresh_from_db()
        assert Defecto.objects.filter(id=bug.id).exists()
        assert bug.historia_usuario is None
        assert not HistoriaUsuario.objects.filter(id=hu.id).exists()

    def test_eliminar_equipo_no_borra_el_defecto(self, client):
        equipo = Equipo.objects.create(nombre_equipo="Equipo A", lider="Juan")
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="desc", equipo=equipo)

        client.post(reverse('eliminar_equipo', args=[equipo.id]))

        bug.refresh_from_db()
        assert Defecto.objects.filter(id=bug.id).exists()
        assert bug.equipo is None
        assert not Equipo.objects.filter(id=equipo.id).exists()


@pytest.mark.django_db
class TestExportacion:

    def test_exportar_defectos_incluye_todos_los_bugs(self, client):
        Defecto.objects.create(titulo="Bug 1", descripcion="d1")
        Defecto.objects.create(titulo="Bug 2", descripcion="d2")
        response = client.get(reverse('exportar_defectos'))
        assert response.status_code == 200
        contenido = response.content.decode()
        assert "Bug 1" in contenido
        assert "Bug 2" in contenido