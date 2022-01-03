# Generated by Django 3.2.4 on 2021-12-08 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0149_alter_arcinstance_amount_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverdisk',
            name='controller',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3)], default=0),
        ),
        migrations.AddField(
            model_name='serverdisk',
            name='device',
            field=models.IntegerField(default=1),
        ),
    ]
