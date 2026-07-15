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
    crear_sprint,
    cerrar_sprint,
    asignar_sprint,
    historial_sprints,
    exportar_sprint,
    exportar_defectos,
    marcar_notificaciones_leidas,
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
    path('sprint/crear/', crear_sprint, name='crear_sprint'),
    path('sprint/<int:sprint_id>/cerrar/', cerrar_sprint, name='cerrar_sprint'),
    path('bug/<int:bug_id>/asignar-sprint/', asignar_sprint, name='asignar_sprint'),
    path('sprints/', historial_sprints, name='historial_sprints'),
    path('sprint/<int:sprint_id>/exportar/', exportar_sprint, name='exportar_sprint'),
    path('defectos/exportar/', exportar_defectos, name='exportar_defectos'),
    path('notificaciones/marcar-leidas/', marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),
]