# Generated by Django 5.0.2 on 2025-03-04 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk_assessment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='category',
            field=models.CharField(choices=[('Construction', 'Construction'), ('Event Management', 'Event Management'), ('Healthcare', 'Healthcare'), ('Education', 'Education'), ('Hospitality', 'Hospitality'), ('Retail', 'Retail'), ('Other', 'Other')], max_length=100),
        ),
    ]
