# Generated by Django 5.1.6 on 2025-03-05 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0008_alter_pelicula_favorita_alter_pelicula_vista_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pelicula',
            old_name='año',
            new_name='anio',
        ),
        migrations.RenameField(
            model_name='serie',
            old_name='año',
            new_name='anio',
        ),
    ]
