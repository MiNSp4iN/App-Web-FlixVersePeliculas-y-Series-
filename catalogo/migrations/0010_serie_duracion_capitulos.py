# Generated by Django 5.1.6 on 2025-03-05 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0009_rename_año_pelicula_anio_rename_año_serie_anio'),
    ]

    operations = [
        migrations.AddField(
            model_name='serie',
            name='duracion_capitulos',
            field=models.IntegerField(null=True),
        ),
    ]
