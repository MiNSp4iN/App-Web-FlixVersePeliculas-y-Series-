#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    portada = models.ImageField(upload_to='categorias', null=True, blank=True)
    
    def __str__(self):
        return self.nombre

class Pelicula(models.Model):
    portada = models.ImageField(upload_to='peliculas', null=True, blank=True)
    #upload_to: carpeta donde se guardan las imagenes
    titulo = models.CharField(max_length=100)
    anio = models.IntegerField(null=True)
    director = models.CharField(max_length=100, null=True)
    sinopsis = models.TextField()
    duracion = models.IntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    vista = models.ManyToManyField(User, related_name="peliculas_vistas", blank=True)
    favorita = models.ManyToManyField(User,related_name="peliculas_favoritas", blank=True)
    trailer_url = models.URLField(blank=True, null=True)
    #user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class Serie(models.Model):
    portada = models.ImageField(upload_to='series', null=True, blank=True)
    titulo = models.CharField(max_length=100)
    anio = models.IntegerField(null=True)
    creador_creadores = models.CharField(max_length=100, null=True)
    sinopsis = models.TextField()
    temporadas = models.IntegerField()
    numero_capitulos = models.IntegerField()
    duracion_capitulos= models.IntegerField(null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    vista = models.ManyToManyField(User, related_name="series_vistas", blank=True)
    favorita = models.ManyToManyField(User, related_name="series_favoritas", blank=True)
    trailer_url = models.URLField(blank=True, null=True)
    #user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
    
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)
    
    def duration(self):
        if self.logout_time:  
            duration = (self.logout_time - self.login_time).total_seconds() / 60.0
            return max(duration, 0)
        return 0 
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    




