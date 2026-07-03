from django.shortcuts import render, redirect, get_object_or_404
from .models import HistoriaUsuario, Defecto, Equipo

def tablero_kanban(request):
    if request.method == 'POST':

        if 'codigo_hu' in request.POST:
            codigo = request.POST.get('codigo_hu')
            descripcion = request.POST.get('descripcion_hu')
            if codigo and descripcion:
                HistoriaUsuario.objects.create(codigo_hu=codigo, descripcion_hu=descripcion)
            return redirect('tablero')

        elif 'titulo_bug' in request.POST:
            titulo = request.POST.get('titulo_bug')
            descripcion = request.POST.get('descripcion_bug')
            severidad = request.POST.get('severidad_bug')
            hu_codigo = request.POST.get('hu_asociada')

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

        elif 'nombre_equipo' in request.POST:
            nombre = request.POST.get('nombre_equipo')
            lider = request.POST.get('lider_equipo')
            integrantes = request.POST.get('integrantes_equipo')
            if nombre and lider and integrantes:
                Equipo.objects.create(nombre=nombre, lider=lider, integrantes=integrantes)
            return redirect('tablero')

        # Caso D: Asignar equipo a un bug existente
        elif 'asignar_equipo_bug_id' in request.POST:
            bug_id = request.POST.get('asignar_equipo_bug_id')
            equipo_id = request.POST.get('equipo_asignado')
            bug = get_object_or_404(Defecto, id=bug_id)
            if equipo_id:
                bug.equipo = get_object_or_404(Equipo, id=equipo_id)
                bug.save()
            return redirect('tablero')

    bugs = Defecto.objects.all()
    hus = HistoriaUsuario.objects.all()
    equipos = Equipo.objects.all()

    return render(request, 'index.html', {'bugs': bugs, 'hus': hus, 'equipos': equipos})