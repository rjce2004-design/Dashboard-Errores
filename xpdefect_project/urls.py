from django.contrib import admin
from django.urls import path
from kanban.views import tablero_kanban  # Importamos tu vista

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tablero_kanban, name='tablero'),  # Ruta de la página principal
]