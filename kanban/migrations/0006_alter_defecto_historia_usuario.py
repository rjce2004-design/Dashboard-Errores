import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0005_historial_notificacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defecto',
            name='historia_usuario',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='kanban.historiausuario',
            ),
        ),
    ]