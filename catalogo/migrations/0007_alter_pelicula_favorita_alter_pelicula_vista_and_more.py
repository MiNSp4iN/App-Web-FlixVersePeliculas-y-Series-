# Generated by Django 5.1.6 on 2025-03-04 17:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0006_remove_pelicula_favorita_remove_pelicula_vista_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='pelicula',
            name='favorita',
            field=models.ManyToManyField(blank=True, related_name='pelicula_favorita', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pelicula',
            name='vista',
            field=models.ManyToManyField(blank=True, related_name='pelicula_vista', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='serie',
            name='favorita',
            field=models.ManyToManyField(blank=True, related_name='serie_favorita', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='serie',
            name='vista',
            field=models.ManyToManyField(blank=True, related_name='serie_vista', to=settings.AUTH_USER_MODEL),
        ),
    ]
