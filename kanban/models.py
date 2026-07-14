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
        """Devuelve los nombres de los integrantes como una lista limpia."""
        return [nombre.strip() for nombre in self.integrantes.split(',') if nombre.strip()]


class Defecto(models.Model):
    ESTADOS = [
        ('ABIERTO', '1. Abierto'),
        ('ANALISIS', '2. En Análisis'),
        ('CORRECCION', '3. En Corrección'),
        ('RESUELTO', '4. Resuelto'),
        ('CERRADO', '5. Cerrado'),
    ]

    # Orden secuencial de los estados, usado para "avanzar" un bug a la siguiente columna
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
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bugs'
    )

    def __str__(self):
        return self.titulo

    def siguiente_estado(self):
        """Devuelve (codigo, etiqueta) del siguiente estado, o None si ya está en el último."""
        try:
            idx = self.ORDEN_ESTADOS.index(self.estado)
        except ValueError:
            return None
        if idx < len(self.ORDEN_ESTADOS) - 1:
            siguiente_codigo = self.ORDEN_ESTADOS[idx + 1]
            return dict(self.ESTADOS)[siguiente_codigo], siguiente_codigo
        return None