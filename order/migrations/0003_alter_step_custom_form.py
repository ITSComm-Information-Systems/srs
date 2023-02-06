# Generated by Django 3.2.13 on 2023-02-06 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_alter_userchartcomv_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='custom_form',
            field=models.CharField(blank=True, choices=[('', ''), ('TabForm', 'Base Form'), ('PhoneLocationForm', 'Phone Location'), ('EquipmentForm', 'Equipment'), ('NewLocationForm', 'New Location'), ('AddlInfoForm', 'Additional Information'), ('ReviewForm', 'Review'), ('ChartfieldForm', 'Chartfield'), ('RestrictionsForm', 'Restrictions'), ('FeaturesForm', 'Features'), ('StaticForm', 'Static Page'), ('AuthCodeForm', 'Auth Codes'), ('AuthCodeCancelForm', 'Auth Codes'), ('CMCCodeForm', 'CMC Codes'), ('ProductForm', 'Quantity Model'), ('ContactCenterForm', 'Contact Center'), ('BillingForm', 'Billing'), ('VoicemailForm', 'Voicemail'), ('DetailsCIFSForm', 'CIFS Details'), ('DetailsNFSForm', 'NFS Details'), ('AccessCIFSForm', 'CIFS Access'), ('AccessNFSForm', 'NFS Access'), ('BillingStorageForm', 'Billing'), ('BackupDetailsForm', 'Backup Details'), ('VolumeSelectionForm', 'Volume Selection'), ('SubscriptionSelForm', 'Subscription Selection'), ('DatabaseTypeForm', 'Database Type'), ('DatabaseConfigForm', 'Database Configuration'), ('ServerInfoForm', 'Server Info'), ('ServerSupportForm', 'Server Support'), ('ServerSpecForm', 'Server Specification'), ('ServerDataForm', 'Server Data Sensitivity'), ('DataDenForm', 'Data Den Form'), ('ChangeSFUserForm', 'Change Softphone User')], max_length=20),
        ),
    ]
