import pytest
from django.urls import reverse
from kanban.models import Defecto, Equipo, Desarrollador


@pytest.mark.django_db
class TestPanelMetricas:

    def test_metricas_muestra_etiquetas_traducidas(self, client):
        Defecto.objects.create(titulo="Bug 1", descripcion="d", severidad="ALTA", estado="ABIERTO")
        response = client.get(reverse('panel_metricas'))
        contenido = response.content.decode()

        # Deben aparecer las etiquetas legibles...
        assert "Alta" in contenido
        assert "Abierto" in contenido
        # ...y no los códigos crudos sueltos como texto de la tarjeta de severidad
        assert "ALTA" not in contenido.split('Por Desarrollador')[0].replace("ALTA</option", "")


@pytest.mark.django_db
class TestAsignarEquipoValidacion:

    def test_no_permite_asignar_desarrollador_de_otro_equipo(self, client):
        equipo_a = Equipo.objects.create(nombre_equipo="Equipo A", lider="Ana")
        equipo_b = Equipo.objects.create(nombre_equipo="Equipo B", lider="Beto")
        dev_b = Desarrollador.objects.create(nombre="Carlos", equipo=equipo_b)
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="d")

        client.post(
            reverse('asignar_equipo', args=[bug.id]),
            {'equipo_id': equipo_a.id, 'desarrollador_id': dev_b.id, 'responsable': 'Ana'},
        )

        bug.refresh_from_db()
        assert bug.equipo is None
        assert bug.desarrollador_asignado is None

    def test_permite_asignar_desarrollador_de_su_propio_equipo(self, client):
        equipo_a = Equipo.objects.create(nombre_equipo="Equipo A", lider="Ana")
        dev_a = Desarrollador.objects.create(nombre="Carlos", equipo=equipo_a)
        bug = Defecto.objects.create(titulo="Bug 1", descripcion="d")

        client.post(
            reverse('asignar_equipo', args=[bug.id]),
            {'equipo_id': equipo_a.id, 'desarrollador_id': dev_a.id, 'responsable': 'Ana'},
        )

        bug.refresh_from_db()
        assert bug.equipo_id == equipo_a.id
        assert bug.desarrollador_asignado_id == dev_a.id