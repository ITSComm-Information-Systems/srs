# Generated by Django 3.1.5 on 2021-03-13 21:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_choice_choicetag'),
        ('order', '0129_auto_20210313_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='database',
            name='version',
            field=models.ForeignKey(blank=True, limit_choices_to={'parent__code': 'DATABASE_VERSION'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.choice'),
        ),
        migrations.RemoveField(
            model_name='server',
            name='regulated_data',
        ),
        migrations.AddField(
            model_name='server',
            name='regulated_data',
            field=models.ManyToManyField(blank=True, limit_choices_to={'parent__code': 'REGULATED_SENSITIVE_DATA'}, to='project.Choice'),
        ),
    ]