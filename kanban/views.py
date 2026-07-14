from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import HistoriaUsuario, Defecto, Equipo


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
            equipo_id = request.POST.get('equipo_asignado')

            hu_instancia = None
            if hu_codigo:
                hu_instancia = HistoriaUsuario.objects.filter(codigo_hu=hu_codigo).first()

            equipo_instancia = None
            if equipo_id:
                equipo_instancia = Equipo.objects.filter(id=equipo_id).first()

            if titulo and descripcion:
                Defecto.objects.create(
                    titulo=titulo,
                    descripcion=descripcion,
                    severidad=severidad,
                    estado='ABIERTO',
                    historia_usuario=hu_instancia,
                    equipo=equipo_instancia,
                )
            return redirect('tablero')

    # SI EL USUARIO SOLO ENTRA A VER LA PÁGINA (GET)
    hus = HistoriaUsuario.objects.all()
    equipos = Equipo.objects.all()

    # Armamos las columnas ya ordenadas, con sus bugs filtrados por estado
    columnas = []
    for codigo, etiqueta in Defecto.ESTADOS:
        columnas.append({
            'codigo': codigo,
            'titulo': etiqueta,
            'bugs': Defecto.objects.filter(estado=codigo).select_related('historia_usuario', 'equipo'),
        })

    return render(request, 'index.html', {
        'hus': hus,
        'equipos': equipos,
        'columnas': columnas,
    })


@require_POST
def eliminar_bug(request, bug_id):
    """Elimina un defecto. La confirmación 'estás seguro' se hace en el front (JS) antes de enviar el POST."""
    bug = get_object_or_404(Defecto, id=bug_id)
    bug.delete()
    return redirect('tablero')


@require_POST
def avanzar_estado(request, bug_id):
    """Mueve el bug al siguiente estado del flujo (Abierto -> Análisis -> Corrección -> Resuelto -> Cerrado)."""
    bug = get_object_or_404(Defecto, id=bug_id)
    resultado = bug.siguiente_estado()
    if resultado:
        _, siguiente_codigo = resultado
        bug.estado = siguiente_codigo
        bug.save()
    return redirect('tablero')


@require_POST
def asignar_equipo(request, bug_id):
    """Asigna (o quita) un equipo a un bug ya existente."""
    bug = get_object_or_404(Defecto, id=bug_id)
    equipo_id = request.POST.get('equipo_id')
    if equipo_id:
        bug.equipo = Equipo.objects.filter(id=equipo_id).first()
    else:
        bug.equipo = None
    bug.save()
    return redirect('tablero')


@require_POST
def crear_equipo(request):
    """Crea un nuevo equipo de trabajo con nombre, líder e integrantes."""
    nombre = request.POST.get('nombre_equipo')
    lider = request.POST.get('lider_equipo')
    integrantes = request.POST.get('integrantes_equipo', '')

    if nombre and lider:
        Equipo.objects.create(
            nombre_equipo=nombre,
            lider=lider,
            integrantes=integrantes,
        )
    return redirect('tablero')