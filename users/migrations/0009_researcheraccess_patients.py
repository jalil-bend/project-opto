# Generated by Django 5.1.6 on 2025-02-24 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_researcher_access_code_researcher_license_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='researcheraccess',
            name='patients',
            field=models.ManyToManyField(to='users.patient'),
        ),
    ]
