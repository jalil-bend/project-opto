# Generated by Django 5.0 on 2024-12-08 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Masculin'), ('F', 'Féminin'), ('A', 'Autre')], max_length=1, null=True),
        ),
    ]
