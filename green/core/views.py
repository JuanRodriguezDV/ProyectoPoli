from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST

from .decorators import login_required
from .models import EmpresaRecolectora, Recoleccion, Usuario

# Create your views here.
def pagina_de_inicio (request):
    return render(request, 'home.html')

@csrf_protect
@require_http_methods(["GET", "POST"])
def iniciar_sesion(request):
    if request.method == 'POST':
        correo = (request.POST.get('correo') or '').strip().lower()
        contrasena = request.POST.get('contrasena') or ''
        next_url = request.POST.get('next') or request.GET.get('next')

        if not correo or not contrasena:
            messages.error(request, 'Debes ingresar correo y contraseña.')
            return render(request, 'signin.html', {'correo': correo})

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'signin.html', {'correo': correo})

        if not check_password(contrasena, usuario.contrasena):
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'signin.html', {'correo': correo})

        # Rotar la sesión para mitigar fijación
        request.session.flush()
        request.session.cycle_key()

        request.session['usuario_id'] = usuario.id
        messages.success(request, f'¡Bienvenido, {usuario.nombre}!')

        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('home')

    return render(request, 'signin.html')

@require_POST
def cerrar_sesion(request):
    request.session.flush()
    messages.info(request, 'Sesión cerrada.')
    return redirect('home')

@csrf_protect
@require_http_methods(["GET", "POST"])
def crear_cuenta(request):
    if request.method == 'POST':
        contrasena = request.POST.get('contrasena') or ''
        confirmar  = request.POST.get('confirmar_contrasena') or ''
        next_url   = request.POST.get('next') or request.GET.get('next')

        if contrasena != confirmar:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'signup.html', {'data': request.POST})

        try:
            usuario = Usuario.objects.create(
                documento        = (request.POST.get('documento') or '').strip(),
                nombre           = (request.POST.get('nombre') or '').strip(),
                nombre_usuario   = (request.POST.get('nombre_usuario') or '').strip(),
                fecha_nacimiento = parse_date(request.POST.get('fecha_nacimiento')),
                correo           = (request.POST.get('correo') or '').strip().lower(),
                celular          = (request.POST.get('celular') or '').strip(),
                contrasena       = make_password(contrasena),  # guarda hash
                direccion        = (request.POST.get('direccion') or '').strip(),
                sexo             = (request.POST.get('sexo') or '').strip(),
            )

            request.session.flush()
            request.session.cycle_key()
            request.session['usuario_id'] = usuario.id

            messages.success(request, f'¡Bienvenido, {usuario.nombre}! Cuenta creada y sesión iniciada.')

            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')

        except IntegrityError:
            messages.error(request, 'Documento o correo ya están registrados.')
        except Exception as e:
            messages.error(request, f'No se pudo crear la cuenta: {e}')
    return render(request, 'signup.html')

@login_required
def programar_recoleccion (request):
    return render(request, 'request-collection.html')