# Generated by Django 3.1.5 on 2021-03-05 06:40

from django.db import migrations, models
import project.models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0127_remove_database_type_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='element',
            name='type',
            field=models.CharField(choices=[('', ''), ('Radio', 'Radio'), ('ST', 'String'), ('Select', 'Select'), ('List', 'List'), ('NU', 'Number'), ('Chart', 'Chartcom'), ('Label', 'Label'), ('Checkbox', 'Checkbox'), ('McGroup', 'MCommunity Group'), ('ShortCode', 'Short Code'), ('Phone', 'Phone Number'), ('Uniqname', 'Uniqname'), ('HTML', 'Static HTML')], max_length=20),
        ),
        migrations.AlterField(
            model_name='server',
            name='backup_time',
            field=models.TimeField(blank=True, null=True, verbose_name='Daily Backup Time'),
        ),
        migrations.AlterField(
            model_name='server',
            name='patch_day',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='patch_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='reboot_day',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')], null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='reboot_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='shortcode',
            field=project.models.ShortCodeField(help_text='Six digit shortcode for billing purposes.', max_length=6, validators=[project.models.validate_shortcode]),
        ),
        migrations.AlterField(
            model_name='step',
            name='custom_form',
            field=models.CharField(blank=True, choices=[('', ''), ('TabForm', 'Base Form'), ('PhoneLocationForm', 'Phone Location'), ('EquipmentForm', 'Equipment'), ('NewLocationForm', 'New Location'), ('AddlInfoForm', 'Additional Information'), ('ReviewForm', 'Review'), ('ChartfieldForm', 'Chartfield'), ('RestrictionsForm', 'Restrictions'), ('FeaturesForm', 'Features'), ('StaticForm', 'Static Page'), ('AuthCodeForm', 'Auth Codes'), ('AuthCodeCancelForm', 'Auth Codes'), ('CMCCodeForm', 'CMC Codes'), ('ProductForm', 'Quantity Model'), ('ContactCenterForm', 'Contact Center'), ('BillingForm', 'Billing'), ('VoicemailForm', 'Voicemail'), ('DetailsCIFSForm', 'CIFS Details'), ('DetailsNFSForm', 'NFS Details'), ('AccessCIFSForm', 'CIFS Access'), ('AccessNFSForm', 'NFS Access'), ('BillingStorageForm', 'Billing'), ('BackupDetailsForm', 'Backup Details'), ('VolumeSelectionForm', 'Volume Selection'), ('SubscriptionSelForm', 'Subscription Selection'), ('DatabaseTypeForm', 'Database Type'), ('ServerInfoForm', 'Server Info'), ('ServerSupportForm', 'Server Support'), ('ServerSpecForm', 'Server Specification'), ('ServerDataForm', 'Server Data Sensitivity'), ('DataDenForm', 'Data Den Form')], max_length=20),
        ),
    ]
