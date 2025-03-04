# Generated by Django 5.0.2 on 2025-03-04 04:55

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(blank=True)),
                ('stand_no', models.CharField(blank=True, max_length=50)),
                ('category', models.CharField(max_length=100)),
                ('activity', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessor_name', models.CharField(max_length=255)),
                ('date_created', models.DateField(default=django.utils.timezone.now)),
                ('hs_name', models.CharField(blank=True, max_length=255)),
                ('hs_position', models.CharField(blank=True, max_length=255)),
                ('hs_contact', models.CharField(blank=True, max_length=255)),
                ('print_name', models.CharField(blank=True, max_length=255)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to='risk_assessment.company')),
            ],
        ),
        migrations.CreateModel(
            name='GeneratedPDF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='risk_assessments/')),
                ('date_generated', models.DateTimeField(auto_now_add=True)),
                ('cloud_url', models.URLField(blank=True, null=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdfs', to='risk_assessment.assessment')),
            ],
        ),
        migrations.CreateModel(
            name='Hazard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hazard', models.CharField(max_length=255)),
                ('severity', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Low', max_length=10)),
                ('probability', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Low', max_length=10)),
                ('persons', models.CharField(max_length=255)),
                ('controls', models.TextField()),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hazards', to='risk_assessment.assessment')),
            ],
        ),
    ]
