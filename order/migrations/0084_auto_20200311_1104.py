# Generated by Django 2.2 on 2020-03-11 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0083_auto_20200305_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='use_ajax',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='element',
            name='type',
            field=models.CharField(choices=[('', ''), ('Radio', 'Radio'), ('ST', 'String'), ('NU', 'Number'), ('Chart', 'Chartcom'), ('Label', 'Label'), ('Checkbox', 'Checkbox'), ('McGroup', 'MCommunity Group'), ('ShortCode', 'Short Code'), ('Phone', 'Phone Number'), ('Uniqname', 'Uniqname'), ('HTML', 'Static HTML')], max_length=20),
        ),
        migrations.AlterField(
            model_name='storageinstance',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Assign Date'),
        ),
    ]
