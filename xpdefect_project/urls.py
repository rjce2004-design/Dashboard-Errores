from django.contrib import admin
from django.urls import path
from kanban.views import (
    tablero_kanban,
    eliminar_bug,
    avanzar_estado,
    asignar_equipo,
    crear_equipo,
    crear_desarrollador,
    crear_prueba,
    panel_metricas,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tablero_kanban, name='tablero'),
    path('bug/<int:bug_id>/eliminar/', eliminar_bug, name='eliminar_bug'),
    path('bug/<int:bug_id>/avanzar/', avanzar_estado, name='avanzar_estado'),
    path('bug/<int:bug_id>/asignar-equipo/', asignar_equipo, name='asignar_equipo'),
    path('equipo/crear/', crear_equipo, name='crear_equipo'),
    path('desarrollador/crear/', crear_desarrollador, name='crear_desarrollador'),
    path('bug/<int:bug_id>/prueba/crear/', crear_prueba, name='crear_prueba'),
    path('metricas/', panel_metricas, name='panel_metricas'),
]