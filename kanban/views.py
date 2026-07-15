from django.http import HttpResponse
from .models import HistoriaUsuario, Defecto, Equipo, Desarrollador, PruebaUnitaria, Sprint
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count


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
            equipo_id = request.POST.get('equipo_asignado')
            desarrollador_id = request.POST.get('desarrollador_asignado')

            hu_instancia = HistoriaUsuario.objects.filter(codigo_hu=hu_codigo).first() if hu_codigo else None
            equipo_instancia = Equipo.objects.filter(id=equipo_id).first() if equipo_id else None
            desarrollador_instancia = (
                Desarrollador.objects.filter(id=desarrollador_id).first() if desarrollador_id else None
            )

            if titulo and descripcion:
                Defecto.objects.create(
                    titulo=titulo,
                    descripcion=descripcion,
                    severidad=severidad,
                    estado='ABIERTO',
                    historia_usuario=hu_instancia,
                    equipo=equipo_instancia,
                    desarrollador_asignado=desarrollador_instancia,
                )
            return redirect('tablero')

    hus = HistoriaUsuario.objects.all()
    equipos = Equipo.objects.all()
    desarrolladores = Desarrollador.objects.all()
    sprints = Sprint.objects.filter(estado='ABIERTO')

    columnas = []
    for codigo, etiqueta in Defecto.ESTADOS:
        columnas.append({
            'codigo': codigo,
            'titulo': etiqueta,
            'bugs': Defecto.objects.filter(estado=codigo).select_related(
                'historia_usuario', 'equipo', 'desarrollador_asignado'
            ).prefetch_related('pruebas'),
        })

    return render(request, 'index.html', {
        'hus': hus,
        'equipos': equipos,
        'desarrolladores': desarrolladores,
        'sprints': sprints,
        'columnas': columnas,
    })


@require_POST
def eliminar_bug(request, bug_id):
    bug = get_object_or_404(Defecto, id=bug_id)
    bug.delete()
    return redirect('tablero')


@require_POST
def avanzar_estado(request, bug_id):
    bug = get_object_or_404(Defecto, id=bug_id)
    resultado = bug.siguiente_estado()
    if resultado:
        _, siguiente_codigo = resultado
        # Requisito 6: no se puede pasar a RESUELTO sin al menos una prueba
        if siguiente_codigo == 'RESUELTO' and not bug.puede_pasar_a_resuelto():
            messages.error(
                request,
                f'No se puede marcar #BUG-{bug.id} como Resuelto: '
                f'registra al menos una prueba unitaria primero.'
            )
            return redirect('tablero')
        bug.estado = siguiente_codigo
        bug.save()
    return redirect('tablero')


@require_POST
def asignar_equipo(request, bug_id):
    bug = get_object_or_404(Defecto, id=bug_id)
    equipo_id = request.POST.get('equipo_id')
    desarrollador_id = request.POST.get('desarrollador_id')

    bug.equipo = Equipo.objects.filter(id=equipo_id).first() if equipo_id else None
    bug.desarrollador_asignado = (
        Desarrollador.objects.filter(id=desarrollador_id).first() if desarrollador_id else None
    )
    bug.save()
    return redirect('tablero')


@require_POST
def crear_equipo(request):
    nombre = request.POST.get('nombre_equipo')
    lider = request.POST.get('lider_equipo')
    integrantes = request.POST.get('integrantes_equipo', '')

    if nombre and lider:
        Equipo.objects.create(nombre_equipo=nombre, lider=lider, integrantes=integrantes)
    return redirect('tablero')


@require_POST
def crear_desarrollador(request):
    nombre = request.POST.get('nombre_desarrollador')
    equipo_id = request.POST.get('equipo_desarrollador')
    equipo_instancia = Equipo.objects.filter(id=equipo_id).first() if equipo_id else None

    if nombre:
        Desarrollador.objects.create(nombre=nombre, equipo=equipo_instancia)
    return redirect('tablero')


@require_POST
def crear_prueba(request, bug_id):
    bug = get_object_or_404(Defecto, id=bug_id)
    nombre_prueba = request.POST.get('nombre_prueba')
    resultado = request.POST.get('resultado_prueba', 'PASO')
    notas = request.POST.get('notas_prueba', '')

    if nombre_prueba:
        PruebaUnitaria.objects.create(
            defecto=bug, nombre_prueba=nombre_prueba, resultado=resultado, notas=notas
        )
    return redirect('tablero')


def panel_metricas(request):
    """Requisito 7: métricas por severidad, por desarrollador y por estado."""
    por_severidad = Defecto.objects.values('severidad').annotate(total=Count('id')).order_by('severidad')
    por_estado = Defecto.objects.values('estado').annotate(total=Count('id')).order_by('estado')
    por_desarrollador = (
        Defecto.objects.values('desarrollador_asignado__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    resueltos_sin_prueba = Defecto.objects.filter(
        estado__in=['RESUELTO', 'CERRADO']
    ).exclude(pruebas__isnull=False).count()

    return render(request, 'metricas.html', {
        'por_severidad': por_severidad,
        'por_estado': por_estado,
        'por_desarrollador': por_desarrollador,
        'resueltos_sin_prueba': resueltos_sin_prueba,
        'severidad_labels': dict(Defecto.SEVERIDADES),
        'estado_labels': dict(Defecto.ESTADOS),
    })

@require_POST
def crear_sprint(request):
    nombre = request.POST.get('nombre_sprint')
    fecha_inicio = request.POST.get('fecha_inicio_sprint')
    fecha_fin = request.POST.get('fecha_fin_sprint')

    if nombre and fecha_inicio and fecha_fin:
        Sprint.objects.create(nombre=nombre, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    return redirect('tablero')


@require_POST
def cerrar_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    sprint.estado = 'CERRADO'
    sprint.save()
    return redirect('historial_sprints')


@require_POST
def asignar_sprint(request, bug_id):
    """Requisito 10: valida que el sprint destino no esté cerrado antes de asignar."""
    bug = get_object_or_404(Defecto, id=bug_id)
    sprint_id = request.POST.get('sprint_id')

    if not sprint_id:
        bug.sprint = None
        bug.save()
        return redirect('tablero')

    sprint = get_object_or_404(Sprint, id=sprint_id)
    if not bug.puede_asignarse_a_sprint(sprint):
        messages.error(
            request,
            f'No se puede asignar #BUG-{bug.id} al sprint "{sprint.nombre}": '
            f'ese sprint ya está cerrado.'
        )
        return redirect('tablero')

    bug.sprint = sprint
    bug.save()
    return redirect('tablero')


def historial_sprints(request):
    """Requisito 8: historial de sprints con sus tareas (defectos) asociadas."""
    sprints = Sprint.objects.all().prefetch_related('defectos')
    return render(request, 'historial_sprints.html', {'sprints': sprints})


def exportar_sprint(request, sprint_id):
    """Requisito 9: exporta el resumen del sprint en texto plano."""
    sprint = get_object_or_404(Sprint, id=sprint_id)
    defectos = sprint.defectos.select_related('desarrollador_asignado', 'equipo').all()

    lineas = []
    lineas.append(f"RESUMEN DE SPRINT: {sprint.nombre}")
    lineas.append(f"Periodo: {sprint.fecha_inicio} a {sprint.fecha_fin}")
    lineas.append(f"Estado: {sprint.get_estado_display()}")
    lineas.append(f"Total de tareas: {defectos.count()}")
    lineas.append("-" * 50)

    for d in defectos:
        dev = d.desarrollador_asignado.nombre if d.desarrollador_asignado else "Sin asignar"
        lineas.append(f"#BUG-{d.id} | {d.titulo}")
        lineas.append(f"  Severidad: {d.get_severidad_display()} | Estado: {d.get_estado_display()}")
        lineas.append(f"  Desarrollador: {dev}")
        lineas.append(f"  Pruebas registradas: {d.pruebas.count()}")
        lineas.append("")

    if not defectos:
        lineas.append("(Este sprint no tiene tareas asociadas)")

    contenido = "\n".join(lineas)
    response = HttpResponse(contenido, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="sprint_{sprint.id}_{sprint.nombre}.txt"'
    return response