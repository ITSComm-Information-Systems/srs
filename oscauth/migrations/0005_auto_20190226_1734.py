# Generated by Django 2.1.5 on 2019-02-26 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oscauth', '0004_auto_20190220_1029'),
    ]

    operations = [
        migrations.CreateModel(
            name='OscAuthUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uniqname', models.CharField(max_length=150)),
                ('deptid', models.CharField(max_length=10)),
                ('role', models.CharField(max_length=30)),
                ('privilege', models.CharField(max_length=30)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('created_by', models.CharField(default='Will be autogenerated', max_length=150)),
            ],
            options={
                'db_table': 'oscauth_auth_user',
            },
        ),
        migrations.RemoveField(
            model_name='roleprivrestriction',
            name='privilege',
        ),
        migrations.RemoveField(
            model_name='roleprivrestriction',
            name='restriction',
        ),
        migrations.RemoveField(
            model_name='roleprivrestriction',
            name='role',
        ),
        migrations.DeleteModel(
            name='Restriction',
        ),
        migrations.DeleteModel(
            name='RolePrivRestriction',
        ),
        migrations.AlterUniqueTogether(
            name='oscauthuser',
            unique_together={('uniqname', 'deptid', 'role', 'privilege')},
        ),
    ]
