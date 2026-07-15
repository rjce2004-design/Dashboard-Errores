import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0002_equipo_and_defecto_equipo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Desarrollador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('equipo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='desarrolladores', to='kanban.equipo')),
            ],
        ),
        migrations.AddField(
            model_name='defecto',
            name='desarrollador_asignado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bugs_asignados', to='kanban.desarrollador'),
        ),
        migrations.CreateModel(
            name='PruebaUnitaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_prueba', models.CharField(max_length=150)),
                ('resultado', models.CharField(choices=[('PASO', 'Pasó'), ('FALLO', 'Falló')], default='PASO', max_length=10)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('notas', models.TextField(blank=True)),
                ('defecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pruebas', to='kanban.defecto')),
            ],
        ),
    ]