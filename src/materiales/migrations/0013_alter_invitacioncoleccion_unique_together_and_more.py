from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiales', '0012_merge_20260716_2052'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='invitacioncoleccion',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='solicitudaccesocoleccion',
            unique_together=set(),
        ),
    ]
