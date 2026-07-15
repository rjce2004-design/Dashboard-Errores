import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0004_sprint'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialEstado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_anterior', models.CharField(blank=True, choices=[('ABIERTO', '1. Abierto'), ('ANALISIS', '2. En Análisis'), ('CORRECCION', '3. En Corrección'), ('RESUELTO', '4. Resuelto'), ('CERRADO', '5. Cerrado')], max_length=15)),
                ('estado_nuevo', models.CharField(choices=[('ABIERTO', '1. Abierto'), ('ANALISIS', '2. En Análisis'), ('CORRECCION', '3. En Corrección'), ('RESUELTO', '4. Resuelto'), ('CERRADO', '5. Cerrado')], max_length=15)),
                ('responsable', models.CharField(blank=True, default='Sin especificar', max_length=100)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('defecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='kanban.defecto')),
            ],
            options={'ordering': ['-fecha']},
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.CharField(max_length=255)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('leida', models.BooleanField(default=False)),
                ('defecto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to='kanban.defecto')),
            ],
            options={'ordering': ['-fecha']},
        ),
    ]