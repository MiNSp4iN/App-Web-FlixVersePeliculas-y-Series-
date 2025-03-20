from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Pelicula, Serie, Categoria, UserSession
from django.db.models import Q
from django.db.models import Sum
from django.utils.timezone import now
from .models import UserSession
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.pyplot as plt
from collections import defaultdict
from django.db.models import Sum
from .models import UserSession
from django.db.models import F,  IntegerField
from django.db.models.functions import Cast
from collections import defaultdict
from django.contrib.admin.views.decorators import staff_member_required



# Create your views here.



# Esta función se ejecuta cuando un usuario inicia sesión. Crea un nuevo objeto UserSession con el usuario que ha iniciado sesión y el momento actual.
def register_login(user):
    UserSession.objects.create(user=user, login_time=now())
    
# Esta función se ejecuta cuando un usuario cierra sesión. Busca la última sesión abierta del usuario y actualiza el campo logout_time con el momento actual.
def register_logout(user):
    session = UserSession.objects.filter(
        user=user, logout_time__isnull=True).last()
    if session:
        session.logout_time = now()
        session.save()


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == "GET":
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('home2')
            except IntegrityError:
                return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'El nombre de usuario ya existe, por favor elige otro nombre'})

        return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Las contraseñas no coinciden'})


def signin(request):
    if request.method == "GET":
        form = AuthenticationForm()
        return render(request, 'signin.html', {'form': form})
    else:
        user = authenticate(
            request, username=request.POST["username"], password=request.POST["password"])
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm(), 'error': 'El nombre de usuario o la contraseña no coinciden'})
        else:
            login(request, user)
            return redirect('home2')


@login_required
def signout(request):
    logout(request)
    return redirect('home')


@login_required
def home2(request):
    return render(request, 'home2.html')

# PELICULAS


@login_required
def lista_peliculas(request):
    peliculas = Pelicula.objects.all()
    return render(request, 'lista_peliculas.html', {'peliculas': peliculas})

# Orden lista películas


@login_required
def peliculas_por_año(request):
    peliculas = Pelicula.objects.order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"
    return render(request, 'lista_peliculas.html', {'peliculas': peliculas, 'mensaje': mensaje})


@login_required
def buscar_peliculas_por_anio(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas = Pelicula.objects.order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"

    peliculas = peliculas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(
        director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas

    if "HX-Request" in request.headers:
        return render(request, 'partials/lista_peliculas.html', {'peliculas': peliculas, 'texto': texto, })
    return render(request, 'lista_peliculas.html', {'peliculas': peliculas, 'texto': texto, 'mensaje': mensaje})


@login_required
def peliculas_por_duracion(request):
    peliculas = Pelicula.objects.order_by('duracion')
    mensaje = "ordenadas por duración, de menor duración a mayor duración"
    return render(request, 'lista_peliculas.html', {'peliculas': peliculas, 'mensaje': mensaje})


@login_required
def buscar_peliculas_por_duracion(request):
    texto = request.GET.get("texto", "").strip(
    ) if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas = Pelicula.objects.order_by('duracion')
    mensaje = "ordenadas por duración, de menor duración a mayor duración"

    peliculas = peliculas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(
        director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas

    if "HX-Request" in request.headers:
        return render(request, 'partials/lista_peliculas.html', {'peliculas': peliculas, 'texto': texto})
    return render(request, 'lista_peliculas.html', {'peliculas': peliculas, 'texto': texto, 'mensaje': mensaje})


# Orden películas categorizadas
@login_required
def peliculas_categorizadas_por_año(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    peliculas_categorizadas = Pelicula.objects.filter(categoria=categoria).order_by('-anio')
    mensaje = "Aquí tienes las películas de {} ordenadas por año de estreno, de más recientes a más antiguas".format(
        categoria.nombre)
    return render(request, 'peliculas_categorizadas.html', {'categoria': categoria, 'peliculas_categorizadas': peliculas_categorizadas, 'mensaje': mensaje})


@login_required
def buscar_peliculas_categorizadas_por_anio(request, categoria_id):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    categoria = get_object_or_404(Categoria, id=categoria_id)
    peliculas_categorizadas = Pelicula.objects.filter(categoria=categoria).order_by('-anio')
    mensaje = "Aquí tienes las películas de {} ordenadas por año de estreno, de más recientes a más antiguas".format(categoria.nombre)

    peliculas_categorizadas = peliculas_categorizadas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas_categorizadas

    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_categorizadas.html', {'categoria': categoria, 'peliculas_categorizadas': peliculas_categorizadas})
    return render(request, 'peliculas_categorizadas.html', {'categoria': categoria, 'peliculas_categorizadas': peliculas_categorizadas, 'mensaje': mensaje})


@login_required
def peliculas_categorizadas_por_duracion(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    peliculas_categorizadas = Pelicula.objects.filter(categoria=categoria).order_by('duracion')
    mensaje = "Aquí tienes las películas de {} ordenadas por duración, de menor duración a mayor duración".format(
        categoria.nombre)
    return render(request, 'peliculas_categorizadas.html', {'categoria': categoria, 'peliculas_categorizadas': peliculas_categorizadas, 'mensaje': mensaje})


@login_required
def buscar_peliculas_categorizadas_por_duracion(request, categoria_id):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    categoria = get_object_or_404(Categoria, id=categoria_id)
    peliculas_categorizadas = Pelicula.objects.filter(categoria=categoria).order_by('duracion')
    mensaje = "Aquí tienes las películas de {} ordenadas por duración, de menor duración a mayor duración".format(
        categoria.nombre)

    peliculas_categorizadas = peliculas_categorizadas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(
        director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas_categorizadas

    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_categorizadas.html', {'categoria': categoria, 'peliculas_categorizadas': peliculas_categorizadas})
    return render(request, 'peliculas_categorizadas.html', {'categoria': categoria, 'peliculas_categorizadas': peliculas_categorizadas, 'mensaje': mensaje})


# Orden películas favoritas
@login_required
def peliculas_favoritas_por_año(request):
    peliculas_favoritas = request.user.peliculas_favoritas.all().order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"
    return render(request, 'peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas, 'mensaje': mensaje})


@login_required
def buscar_peliculas_favoritas_por_anio(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas_favoritas = request.user.peliculas_favoritas.all().order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"

    peliculas_favoritas = peliculas_favoritas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas_favoritas

    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas})
    return render(request, 'peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas, 'mensaje': mensaje})


@login_required
def peliculas_favoritas_por_duracion(request):
    peliculas_favoritas = request.user.peliculas_favoritas.all().order_by('duracion')
    mensaje = "ordenadas por duración, de menor duración a mayor duración"
    return render(request, 'peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas, 'mensaje': mensaje})

@login_required
def buscar_peliculas_favoritas_por_duracion(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas_favoritas = request.user.peliculas_favoritas.all().order_by('duracion')
    mensaje = "ordenadas por duración, de menor duración a mayor duración"

    peliculas_favoritas = peliculas_favoritas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas_favoritas

    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas})
    return render(request, 'peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas, 'mensaje': mensaje})

# Orden películas vistas


@login_required
def peliculas_vistas_por_año(request):
    peliculas_vistas = request.user.peliculas_vistas.all().order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"
    return render(request, 'peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas, 'mensaje': mensaje})

@login_required
def buscar_peliculas_vistas_por_anio(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas_vistas = request.user.peliculas_vistas.all().order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"

    peliculas_vistas = peliculas_vistas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas_vistas
    
    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas})
    return render(request, 'peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas, 'mensaje': mensaje})

@login_required
def peliculas_vistas_por_duracion(request):
    peliculas_vistas = request.user.peliculas_vistas.all().order_by('duracion')
    mensaje = "ordenadas por duración, de menor duración a mayor duración"
    return render(request, 'peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas, 'mensaje': mensaje})

@login_required
def buscar_peliculas_vistas_por_duracion(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas_vistas = request.user.peliculas_vistas.all().order_by('duracion')
    mensaje = "ordenadas por duración, de menor duración a mayor"

    peliculas_vistas = peliculas_vistas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas_vistas

    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas})
    return render(request, 'peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas, 'mensaje': mensaje})


@login_required
def categorias_peliculas(request):
    categorias = Categoria.objects.filter(pelicula__isnull=False).distinct()
    return render(request, 'categorias_peliculas.html', {'categorias': categorias})


@login_required
def peliculas_categorizadas(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    peliculas_categorizadas = Pelicula.objects.filter(categoria=categoria)
    return render(request, 'peliculas_categorizadas.html', {'categoria': categoria, 'peliculas_categorizadas': peliculas_categorizadas})


@login_required
def marcar_pelicula_favorita(request, pelicula_id):
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)
    if request.user in pelicula.favorita.all():
        pelicula.favorita.remove(request.user)
    else:
        pelicula.favorita.add(request.user)
    return redirect('peliculas_favoritas')


@login_required
def marcar_pelicula_vista(request, pelicula_id):
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)
    if request.user in pelicula.vista.all():
        pelicula.vista.remove(request.user)
    else:
        pelicula.vista.add(request.user)
    return redirect('peliculas_vistas')


@login_required
def peliculas_favoritas(request):
    peliculas_favoritas = request.user.peliculas_favoritas.all()
    return render(request, 'peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas})


@login_required
def peliculas_vistas(request):
    peliculas_vistas = request.user.peliculas_vistas.all()
    # Con aggregate(Sum('duracion')) se obtiene la suma de la duración de todas las películas vistas por el usuario logueado. La duración de cada película se obtiene a través del campo duracion del modelo Pelicula. La suma se almacena en la variable suma. ['duracion__sum'] es la clave que se utiliza para acceder al valor de la suma en el diccionario que devuelve aggregate().
    tiempo_viendo_peliculas = Pelicula.objects.filter(
        vista=request.user).aggregate(Sum('duracion'))['duracion__sum']
    tiempo_viendo_peliculas_horas = tiempo_viendo_peliculas // 60
    total_peliculas_vistas = peliculas_vistas.count()
    return render(request, 'peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas, 'tiempo_viendo_peliculas': tiempo_viendo_peliculas, 'total_peliculas_vistas': total_peliculas_vistas, 'tiempo_viendo_peliculas_horas': tiempo_viendo_peliculas_horas})


@login_required
def detalle_pelicula(request, pelicula_id, pelicula_categoria_id):
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)
    peliculas_relacionadas = Pelicula.objects.filter(
        categoria=pelicula_categoria_id).exclude(id=pelicula_id)
    return render(request, 'detalle_pelicula.html', {'pelicula': pelicula, 'peliculas_relacionadas': peliculas_relacionadas})


# SERIES

@login_required
def lista_series(request):
    series = Serie.objects.all()
    return render(request, 'lista_series.html', {'series': series})
# Orden lista series


@login_required
def series_por_año(request):
    series = Serie.objects.order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"
    return render(request, 'lista_series.html', {'series': series, 'mensaje': mensaje})

@login_required
def buscar_series_por_anio(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    series = Serie.objects.order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"

    series= series.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else series

    if "HX-Request" in request.headers:
        return render(request, 'partials/lista_series.html', {'series': series, 'texto': texto})
    return render(request, 'lista_series.html', {'series': series, 'texto': texto, 'mensaje': mensaje})


@login_required
def series_por_duracion(request):
    series = Serie.objects.all()
    # Key es una función que se aplica a cada elemento de la lista para ordenarla, en este caso se ordena por la duración total de la serie. Esta función se aplica a cada serie creando una lista ordenada de menor a mayor.
    series = sorted(series, key=lambda serie: serie.numero_capitulos * serie.duracion_capitulos)
    mensaje = "ordenadas por duración total, de menor duración a mayor duración"
    return render(request, 'lista_series.html', {'series': series, 'series': series, 'mensaje': mensaje})

@login_required
def buscar_series_por_duracion(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    series= Serie.objects.all()
    mensaje = "ordenadas por duración total, de menor duración a mayor duración"

    if texto:
        series = series.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else series

    series = sorted(series, key=lambda serie: serie.numero_capitulos * serie.duracion_capitulos)

    if "HX-Request" in request.headers:
        return render(request, 'partials/lista_series.html', {'series': series, 'texto': texto})
    return render(request, 'lista_series.html', {'series': series, 'texto': texto, 'mensaje': mensaje})

# Orden series categorizadas


@login_required
def series_categorizadas_por_año(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    series_categorizadas = Serie.objects.filter(categoria=categoria).order_by('-anio')
    mensaje = "Aquí tienes las series de {} ordenadas por año de estreno, de más recientes a más antiguas".format(
        categoria.nombre)
    return render(request, 'series_categorizadas.html', {'categoria': categoria, 'series_categorizadas': series_categorizadas, 'mensaje': mensaje})

@login_required
def buscar_series_categorizadas_por_anio(request, categoria_id):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    categoria = get_object_or_404(Categoria, id=categoria_id)
    series_categorizadas = Serie.objects.filter(categoria=categoria).order_by('-anio')
    mensaje = "Aquí tienes las series de {} ordenadas por año de estreno, de más recientes a más antiguas".format(
        categoria.nombre)

    series_categorizadas = series_categorizadas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else series_categorizadas

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_categorizadas.html', {'categoria': categoria, 'series_categorizadas': series_categorizadas})
    return render(request, 'series_categorizadas.html', {'categoria': categoria, 'series_categorizadas': series_categorizadas, 'mensaje': mensaje})

@login_required
def series_categorizadas_por_duracion(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    series = Serie.objects.filter(categoria=categoria)
    series_categorizadas = sorted(series, key=lambda serie: serie.numero_capitulos * serie.duracion_capitulos)
    mensaje = "Aquí tienes las series de {} ordenadas por duración total, de menor duración a mayor duración".format(
        categoria.nombre)
    return render(request, 'series_categorizadas.html', {'categoria': categoria, 'series': series, 'series_categorizadas': series_categorizadas, 'mensaje': mensaje})

@login_required
def buscar_series_categorizadas_por_duracion(request, categoria_id):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    categoria = get_object_or_404(Categoria, id=categoria_id)
    series_categorizadas = Serie.objects.filter(categoria=categoria).annotate(duracion_capitulos_int=Cast('duracion_capitulos', IntegerField()), duracion_total=F('numero_capitulos') * F('duracion_capitulos_int')
    )
    mensaje = "Aquí tienes las series de {} ordenadas por duración total, de menor duración a mayor duración".format(categoria.nombre)

    if texto:
        series_categorizadas = series_categorizadas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto))

    series_categorizadas = series_categorizadas.order_by('duracion_total')    

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_categorizadas.html', {'categoria': categoria, 'series_categorizadas': series_categorizadas})
    return render(request, 'series_categorizadas.html', {'categoria': categoria, 'series_categorizadas': series_categorizadas, 'mensaje': mensaje})


# Orden series favoritas


@login_required
def series_favoritas_por_año(request):
    series_favoritas = request.user.series_favoritas.all().order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"
    return render(request, 'series_favoritas.html', {'series_favoritas': series_favoritas, 'mensaje': mensaje})

@login_required
def buscar_series_favoritas_por_anio(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    series_favoritas = request.user.series_favoritas.all().order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"

    series_favoritas = series_favoritas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else series_favoritas

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_favoritas.html', {'series_favoritas': series_favoritas})
    return render(request, 'series_favoritas.html', {'series_favoritas': series_favoritas, 'mensaje': mensaje})


@login_required
def series_favoritas_por_duracion(request):
    series_favoritas = request.user.series_favoritas.all()
    series = sorted(series_favoritas, key=lambda serie: serie.numero_capitulos * serie.duracion_capitulos)
    mensaje = "ordenadas por duración total, de menor duración a mayor duración"
    return render(request, 'series_favoritas.html', {'series': series, 'series_favoritas': series_favoritas, 'mensaje': mensaje})

@login_required
def buscar_series_favoritas_por_duracion(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    series_favoritas = request.user.series_favoritas.all()
    mensaje = "ordenadas por duración total, de menor duración a mayor duración"
    
    if texto:
        series_favoritas = series_favoritas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else series_favoritas

    series_favoritas = sorted(series_favoritas, key=lambda serie: serie.numero_capitulos * serie.duracion_capitulos)

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_favoritas.html', {'series_favoritas': series_favoritas})
    return render(request, 'series_favoritas.html', {'series_favoritas': series_favoritas, 'mensaje': mensaje})

# Orden series vistas


@login_required
def series_vistas_por_año(request):
    series_vistas = request.user.series_vistas.all().order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"
    return render(request, 'series_vistas.html', {'series_vistas': series_vistas, 'mensaje': mensaje})

@login_required
def buscar_series_vistas_por_anio(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    series_vistas = request.user.series_vistas.all().order_by('-anio')
    mensaje = "ordenadas por año de estreno, de más recientes a más antiguas"

    series_vistas = series_vistas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else series_vistas

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_vistas.html', {'series_vistas': series_vistas})
    return render(request, 'series_vistas.html', {'series_vistas': series_vistas, 'mensaje': mensaje})


@login_required
def series_vistas_por_duracion(request):
    series_vistas = request.user.series_vistas.all()
    series = sorted(series_vistas, key=lambda serie: serie.numero_capitulos * serie.duracion_capitulos)
    mensaje = "ordenadas por duración total, de menor duración a mayor duración"
    return render(request, 'series_vistas.html', {'series': series, 'series_vistas': series_vistas, 'mensaje': mensaje})

@login_required
def buscar_series_vistas_por_duracion(request):
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    series_vistas = request.user.series_vistas.all()
    mensaje = "ordenadas por duración total, de menor duración a mayor duración"

    if texto:
        series_vistas = series_vistas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else series_vistas

    series_vistas = sorted(series_vistas, key=lambda serie: serie.numero_capitulos * serie.duracion_capitulos)

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_vistas.html', {'series_vistas': series_vistas})
    return render(request, 'series_vistas.html', {'series_vistas': series_vistas, 'mensaje': mensaje})


@login_required
def categorias_series(request):
    categorias = Categoria.objects.filter(serie__isnull=False).distinct()
    return render(request, 'categorias_series.html', {'categorias': categorias})


@login_required
def series_categorizadas(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    series_categorizadas = Serie.objects.filter(categoria=categoria)
    return render(request, 'series_categorizadas.html', {'categoria': categoria, 'series_categorizadas': series_categorizadas})


@login_required
def marcar_serie_favorita(request, serie_id):
    serie = get_object_or_404(Serie, id=serie_id)
    if request.user in serie.favorita.all():
        serie.favorita.remove(request.user)
    else:
        serie.favorita.add(request.user)
    return redirect('series_favoritas')


@login_required
def marcar_serie_vista(request, serie_id):
    serie = get_object_or_404(Serie, id=serie_id)
    if request.user in serie.vista.all():
        serie.vista.remove(request.user)
    else:
        serie.vista.add(request.user)
    return redirect('series_vistas')


@login_required
def series_favoritas(request):
    series_favoritas = request.user.series_favoritas.all()
    return render(request, 'series_favoritas.html', {'series_favoritas': series_favoritas})


@login_required
def series_vistas(request):
    # request.user.series_vistas.all() es una lista de series vistas por el usuario logueado que se obtiene a partir de la relación ManyToManyField en el modelo Serie. Se accede a través del atributo series_vistas del objeto request.user. series_vistas es el related_name que se le asignó a la relación en el modelo Serie.
    series_vistas = request.user.series_vistas.all()
    tiempo_viendo_series = sum(
        serie.numero_capitulos * serie.duracion_capitulos for serie in series_vistas)
    total_series_vistas = series_vistas.count()
    total_temporadas_vistas = sum(serie.temporadas for serie in series_vistas)
    tiempo_viendo_series_horas = tiempo_viendo_series // 60
    total_capitulos_vistos = sum(
        serie.numero_capitulos for serie in series_vistas)
    return render(request, 'series_vistas.html', {'series_vistas': series_vistas, 'tiempo_viendo_series': tiempo_viendo_series, 'total_series_vistas': total_series_vistas, 'total_temporadas_vistas': total_temporadas_vistas, 'total_capitulos_vistos': total_capitulos_vistos, 'tiempo_viendo_series_horas': tiempo_viendo_series_horas})


@login_required
def detalle_serie(request, serie_id, serie_categoria_id):
    serie = get_object_or_404(Serie, id=serie_id)
    series_relacionadas = Serie.objects.filter(
        categoria=serie_categoria_id).exclude(id=serie_id)
    return render(request, 'detalle_serie.html', {'serie': serie, 'series_relacionadas': series_relacionadas})



@login_required
def buscar_pelicula(request):
    texto = request.GET.get("texto", "").strip(
    ) if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas = Pelicula.objects.all()

    peliculas = peliculas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(
        director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas

    if "HX-Request" in request.headers:
        return render(request, 'partials/lista_peliculas.html', {'peliculas': peliculas, 'texto': texto})

    return render(request, 'lista_peliculas.html', {'peliculas': peliculas, 'texto': texto})


@login_required
def buscar_peliculas_categorizadas(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    texto = request.GET.get("texto", "").strip() if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas_categorizadas = Pelicula.objects.filter(categoria=categoria)
    peliculas_categorizadas = peliculas_categorizadas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(director__icontains=texto) | Q(sinopsis__icontains=texto)) if texto else peliculas_categorizadas

    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_categorizadas.html', {'peliculas_categorizadas': peliculas_categorizadas, 'categoria': categoria})
    return render(request, 'peliculas_categorizadas.html', {'categoria': categoria, 'peliculas_categorizadas': peliculas_categorizadas})


@login_required
def buscar_peliculas_favoritas(request):
    texto = request.GET.get("texto", "").strip(
    ) if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas_favoritas = request.user.peliculas_favoritas.all()
    peliculas_favoritas = peliculas_favoritas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(director__icontains=texto) | Q(sinopsis__icontains=texto)
    ) if texto else peliculas_favoritas

    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas})
    return render(request, 'peliculas_favoritas.html', {'peliculas_favoritas': peliculas_favoritas})


@login_required
def buscar_peliculas_vistas(request):
    texto = request.GET.get("texto", "").strip(
    ) if request.method == "GET" else request.POST.get("texto", "").strip()
    peliculas_vistas = Pelicula.objects.filter(vista=request.user)
    peliculas_vistas = peliculas_vistas.filter((Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(director__icontains=texto) | Q(sinopsis__icontains=texto))
    ) if texto else peliculas_vistas

    if "HX-Request" in request.headers:
        return render(request, 'partials/peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas})
    return render(request, 'peliculas_vistas.html', {'peliculas_vistas': peliculas_vistas})


@login_required
def buscar_serie(request):
    texto = request.GET.get("texto", "").strip(
    ) if request.method == "GET" else request.POST.get("texto", "").strip()
    series = Serie.objects.all()
    series = series.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(
            creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)
    ) if texto else series

    if "HX-Request" in request.headers:
        return render(request, 'partials/lista_series.html', {'series': series})
    return render(request, 'lista_series.html', {'series': series})


@login_required
def buscar_series_categorizadas(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    texto = request.GET.get("texto", "").strip(
    ) if request.method == "GET" else request.POST.get("texto", "").strip()
    series_categorizadas = Serie.objects.filter(categoria=categoria)
    series_categorizadas = series_categorizadas.filter((Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto))
    ) if texto else series_categorizadas

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_categorizadas.html', {'series_categorizadas': series_categorizadas, 'categoria': categoria})
    return render(request, 'series_categorizadas.html', {'categoria': categoria, 'series_categorizadas': series_categorizadas})


@login_required
def buscar_series_favoritas(request):
    texto = request.GET.get("texto", "").strip(
    ) if request.method == "GET" else request.POST.get("texto", "").strip()
    series_favoritas = request.user.series_favoritas.all()
    series_favoritas = series_favoritas.filter(Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto)
    ) if texto else series_favoritas

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_favoritas.html', {'series_favoritas': series_favoritas})
    return render(request, 'series_favoritas.html', {'series_favoritas': series_favoritas})


@login_required
def buscar_series_vistas(request):
    texto = request.GET.get("texto", "").strip(
    ) if request.method == "GET" else request.POST.get("texto", "").strip()
    series_vistas = Serie.objects.filter(vista=request.user)
    series_vistas = series_vistas.filter((Q(titulo__icontains=texto) | Q(anio__icontains=texto) | Q(creador_creadores__icontains=texto) | Q(sinopsis__icontains=texto))
    ) if texto else series_vistas

    if "HX-Request" in request.headers:
        return render(request, 'partials/series_vistas.html', {'series_vistas': series_vistas})
    return render(request, 'series_vistas.html', {'series_vistas': series_vistas})


@login_required
def grafico_tiempo_usuario(request):
    # Filtrar sesiones cerradas del usuario
    sesiones = UserSession.objects.filter(user=request.user, logout_time__isnull=False) #esta definicion de sesiones significa que se obtienen todas las sesiones cerradas del usuario logueado

    if not sesiones.exists():
        return render(request, 'grafico_tiempo_usuario.html', {'chart': None, "mensaje": "Todavía no tienes registrado ningún tiempo de sesión."})

    # Agrupar sesiones por fecha y sumar el tiempo total
    tiempo_por_dia = defaultdict(int)
    
    for sesion in sesiones:
        fecha = sesion.login_time.strftime("%Y-%m-%d")  # Solo la fecha sin hora
        tiempo_por_dia[fecha] += sesion.duration()  # Sumar duración total del día

    # Ordenar las fechas
    fechas_ordenadas = sorted(tiempo_por_dia.keys())
    tiempos = [tiempo_por_dia[fecha] for fecha in fechas_ordenadas]

    # Graficar
    plt.figure(figsize=(8, 4))
    plt.plot(fechas_ordenadas, tiempos, marker="o", linestyle="-", color='skyblue', label="Minutos en la app")

    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Fecha')
    plt.ylabel('Tiempo total (minutos)')
    plt.title('Tiempo total en la web por día')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    # Guardar imagen como base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return render(request, 'grafico_tiempo_usuario.html', {'chart': image_base64})


@staff_member_required
def grafico_tiempo_admin(request):
    sesiones = UserSession.objects.filter(logout_time__isnull=False)

    if not sesiones.exists():
        return render(request, 'grafico_tiempo_admin.html', {'chart': None, "mensaje": "No hay datos de sesiones disponibles."})

    tiempo_por_usuario = defaultdict(int)

    for sesion in sesiones:
        tiempo_por_usuario[sesion.user.username] += sesion.duration()

    usuarios_ordenados = sorted(tiempo_por_usuario, key=tiempo_por_usuario.get, reverse=True)
    tiempos = [tiempo_por_usuario[user] for user in usuarios_ordenados]

    plt.figure(figsize=(10, 5))
    plt.bar(usuarios_ordenados, tiempos, color='skyblue')

    plt.xlabel('Usuarios')
    plt.ylabel('Tiempo total (minutos)')
    plt.title('Tiempo total de sesión por usuario')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return render(request, 'grafico_tiempo_admin.html', {'chart': image_base64})

