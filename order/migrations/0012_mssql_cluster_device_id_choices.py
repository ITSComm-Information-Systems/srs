from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_mssql_cluster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mssqlclusterdisk',
            name='device_id',
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, '0'),
                    (1, '1'),
                    (2, '2'),
                    (3, '3'),
                    (4, '4'),
                    (5, '5'),
                    (6, '6'),
                    (8, '8'),
                    (9, '9'),
                    (10, '10'),
                    (11, '11'),
                    (12, '12'),
                    (13, '13'),
                    (14, '14'),
                    (15, '15'),
                ],
            ),
        ),
    ]