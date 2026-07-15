from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count
from .models import HistoriaUsuario, Defecto, Equipo, Desarrollador, PruebaUnitaria


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