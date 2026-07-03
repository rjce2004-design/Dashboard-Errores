from django.db import models

class HistoriaUsuario(models.Model):
    codigo_hu = models.CharField(max_length=10, unique=True)
    descripcion_hu = models.TextField()

    def __str__(self):
        return f"{self.codigo_hu}: {self.descripcion_hu[:30]}..."

class Defecto(models.Model):
    ESTADOS = [
        ('ABIERTO', '1. Abierto'),
        ('ANALISIS', '2. En Análisis'),
        ('CORRECCION', '3. En Corrección'),
        ('RESUELTO', '4. Resuelto'),
        ('CERRADO', '5. Cerrado'),
    ]
    
    SEVERIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    severidad = models.CharField(max_length=10, choices=SEVERIDADES, default='MEDIA')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='ABIERTO')
    historia_usuario = models.ForeignKey(HistoriaUsuario, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.titulo