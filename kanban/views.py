from django.shortcuts import render, redirect
from .models import HistoriaUsuario, Defecto

def tablero_kanban(request):
    # SI EL USUARIO ENVÍA UN FORMULARIO (POST)
    if request.method == 'POST':
        
        # Caso A: Viene del formulario de Nueva HU
        if 'codigo_hu' in request.POST:
            codigo = request.POST.get('codigo_hu')
            descripcion = request.POST.get('descripcion_hu')
            if codigo and descripcion:
                HistoriaUsuario.objects.create(codigo_hu=codigo, descripcion_hu=descripcion)
            return redirect('tablero')
        
        # Caso B: Viene del formulario de Nuevo Bug
        elif 'titulo_bug' in request.POST:
            titulo = request.POST.get('titulo_bug')
            descripcion = request.POST.get('descripcion_bug')
            severidad = request.POST.get('severidad_bug')
            hu_codigo = request.POST.get('hu_asociada')
            
            # Buscamos si la HU seleccionada existe en la Base de Datos
            hu_instancia = None
            if hu_codigo:
                hu_instancia = HistoriaUsuario.objects.filter(codigo_hu=hu_codigo).first()
            
            if titulo and descripcion:
                Defecto.objects.create(
                    titulo=titulo,
                    descripcion=descripcion,
                    severidad=severidad,
                    estado='ABIERTO',
                    historia_usuario=hu_instancia
                )
            return redirect('tablero')

    # SI EL USUARIO SOLO ENTRA A VER LA PÁGINA (GET)
    # Traemos todos los datos reales guardados en la base de datos
    bugs = Defecto.objects.all()
    hus = HistoriaUsuario.objects.all()
    
    # Se los mandamos al HTML index.html
    return render(request, 'index.html', {'bugs': bugs, 'hus': hus})