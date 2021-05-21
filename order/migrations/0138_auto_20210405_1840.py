# Generated by Django 3.1.5 on 2021-04-05 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0137_auto_20210318_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='arguments',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='element',
            name='type',
            field=models.CharField(choices=[('', ''), ('Radio', 'Radio'), ('ST', 'String'), ('Select', 'Select'), ('List', 'List'), ('NU', 'Number'), ('Chart', 'Chartcom'), ('Label', 'Label'), ('Checkbox', 'Checkbox'), ('McGroup', 'MCommunity Group'), ('ShortCode', 'Short Code'), ('Phone', 'Phone Number'), ('Uniqname', 'Uniqname'), ('HTML', 'Static HTML'), ('EmailField', 'Email')], max_length=20),
        ),
    ]