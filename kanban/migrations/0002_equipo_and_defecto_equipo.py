import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_equipo', models.CharField(max_length=100, unique=True)),
                ('lider', models.CharField(max_length=100)),
                ('integrantes', models.TextField(blank=True, help_text='Nombres de los integrantes separados por comas')),
            ],
        ),
        migrations.AddField(
            model_name='defecto',
            name='equipo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bugs',
                to='kanban.equipo',
            ),
        ),
    ]