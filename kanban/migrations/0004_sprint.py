import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0003_desarrollador_prueba'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('estado', models.CharField(choices=[('ABIERTO', 'Abierto'), ('CERRADO', 'Cerrado')], default='ABIERTO', max_length=10)),
            ],
            options={'ordering': ['-fecha_inicio']},
        ),
        migrations.AddField(
            model_name='defecto',
            name='sprint',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='defectos', to='kanban.sprint'),
        ),
    ]