from django.contrib import admin
from django.urls import path
from kanban.views import (
    tablero_kanban,
    eliminar_bug,
    avanzar_estado,
    asignar_equipo,
    crear_equipo,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tablero_kanban, name='tablero'),  # Ruta de la página principal
    path('bug/<int:bug_id>/eliminar/', eliminar_bug, name='eliminar_bug'),
    path('bug/<int:bug_id>/avanzar/', avanzar_estado, name='avanzar_estado'),
    path('bug/<int:bug_id>/asignar-equipo/', asignar_equipo, name='asignar_equipo'),
    path('equipo/crear/', crear_equipo, name='crear_equipo'),
]