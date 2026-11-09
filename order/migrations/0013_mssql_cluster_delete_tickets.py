from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0012_mssql_cluster_device_id_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='mssqlcluster',
            name=field_name,
            field=models.PositiveIntegerField(null=True, blank=True),
        )
        for field_name in (
            'delete_cluster_ticket_id',
            'delete_primary_ticket_id',
            'delete_secondary_ticket_id',
        )
    ]