from django.contrib import admin
from .models import Categoria, Pelicula, Serie
from django.utils.html import format_html
from .models import UserSession
import matplotlib.pyplot as plt
import io
import base64
from django.urls import reverse

class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'duracion_minutos', 'ver_grafico')

    def duracion_minutos(self, obj):
        return obj.duration()
    
    duracion_minutos.short_description = "Duración (min)"

    def ver_grafico(self, obj=None):
        """ Agrega un enlace en el panel de admin para ver el gráfico de tiempo de los usuarios. """
        url = reverse('grafico_tiempo_admin')
        return format_html(f'<a href="{url}" target="_blank">📊 Ver gráfico de tiempos</a>')

    ver_grafico.short_description = "Gráfico de tiempos"







# Register your models here.
admin.site.register(Categoria)
admin.site.register(Pelicula)
admin.site.register(Serie)
admin.site.register(UserSession, UserSessionAdmin)