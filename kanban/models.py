from django.db import models


class HistoriaUsuario(models.Model):
    codigo_hu = models.CharField(max_length=10, unique=True)
    descripcion_hu = models.TextField()

    def __str__(self):
        return f"{self.codigo_hu}: {self.descripcion_hu[:30]}..."


class Equipo(models.Model):
    nombre_equipo = models.CharField(max_length=100, unique=True)
    lider = models.CharField(max_length=100)
    integrantes = models.TextField(
        blank=True,
        help_text="Nombres de los integrantes separados por comas"
    )

    def __str__(self):
        return self.nombre_equipo

    def lista_integrantes(self):
        return [nombre.strip() for nombre in self.integrantes.split(',') if nombre.strip()]


class Desarrollador(models.Model):
    nombre = models.CharField(max_length=100)
    equipo = models.ForeignKey(
        Equipo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='desarrolladores'
    )

    def __str__(self):
        return self.nombre


class Defecto(models.Model):
    ESTADOS = [
        ('ABIERTO', '1. Abierto'),
        ('ANALISIS', '2. En Análisis'),
        ('CORRECCION', '3. En Corrección'),
        ('RESUELTO', '4. Resuelto'),
        ('CERRADO', '5. Cerrado'),
    ]
    ORDEN_ESTADOS = ['ABIERTO', 'ANALISIS', 'CORRECCION', 'RESUELTO', 'CERRADO']
    SEVERIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    severidad = models.CharField(max_length=10, choices=SEVERIDADES, default='MEDIA')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='ABIERTO')
    historia_usuario = models.ForeignKey(
        HistoriaUsuario, on_delete=models.CASCADE, null=True, blank=True
    )
    equipo = models.ForeignKey(
        Equipo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bugs'
    )
    desarrollador_asignado = models.ForeignKey(
        Desarrollador, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bugs_asignados'
    )
    sprint = models.ForeignKey(
        'Sprint', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='defectos'
    )

    def __str__(self):
        return self.titulo

    def siguiente_estado(self):
        try:
            idx = self.ORDEN_ESTADOS.index(self.estado)
        except ValueError:
            return None
        if idx < len(self.ORDEN_ESTADOS) - 1:
            siguiente_codigo = self.ORDEN_ESTADOS[idx + 1]
            return dict(self.ESTADOS)[siguiente_codigo], siguiente_codigo
        return None

    def tiene_prueba_registrada(self):
        return self.pruebas.exists()

    def puede_pasar_a_resuelto(self):
        """Regla: un defecto solo puede marcarse RESUELTO si tiene ≥1 prueba registrada."""
        return self.tiene_prueba_registrada()
    def puede_asignarse_a_sprint(self, sprint):
        """Requisito 10: no se puede asignar una tarea a un sprint ya cerrado."""
        if sprint is None:
            return True
        return sprint.estado != 'CERRADO'


class HistorialEstado(models.Model):
    """Requisito 8: historial de cambios de estado por defecto, con fecha y responsable."""

    defecto = models.ForeignKey(Defecto, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=15, choices=Defecto.ESTADOS, blank=True)
    estado_nuevo = models.CharField(max_length=15, choices=Defecto.ESTADOS)
    responsable = models.CharField(max_length=100, blank=True, default='Sin especificar')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"#{self.defecto_id}: {self.estado_anterior or '—'} → {self.estado_nuevo} ({self.responsable})"


class Notificacion(models.Model):
    """Requisito 9: notificación interna al asignar o cambiar el estado de un defecto."""

    defecto = models.ForeignKey(
        Defecto, on_delete=models.CASCADE, related_name='notificaciones', null=True, blank=True
    )
    mensaje = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return self.mensaje


class PruebaUnitaria(models.Model):
    RESULTADOS = [
        ('PASO', 'Pasó'),
        ('FALLO', 'Falló'),
    ]

    defecto = models.ForeignKey(Defecto, on_delete=models.CASCADE, related_name='pruebas')
    nombre_prueba = models.CharField(max_length=150)
    resultado = models.CharField(max_length=10, choices=RESULTADOS, default='PASO')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre_prueba} ({self.get_resultado_display()})"

class Sprint(models.Model):
    ESTADOS_SPRINT = [
        ('ABIERTO', 'Abierto'),
        ('CERRADO', 'Cerrado'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADOS_SPRINT, default='ABIERTO')

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"

    class Meta:
        ordering = ['-fecha_inicio']