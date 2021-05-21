# Generated by Django 3.1.5 on 2021-04-13 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_choice_choicetag'),
        ('order', '0140_auto_20210413_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='patch_day',
            field=models.ForeignKey(blank=True, limit_choices_to={'parent__code': 'SERVER_PATCH_DAY'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='patch_day', to='project.choice'),
        ),
        migrations.AlterField(
            model_name='server',
            name='reboot_day',
            field=models.ForeignKey(blank=True, limit_choices_to={'parent__code': 'SERVER_REBOOT_DAY'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reboot_day', to='project.choice'),
        ),
    ]