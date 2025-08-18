from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q
from django.core.paginator import Paginator

from .decorators import login_required
from .models import Recoleccion, Usuario
from .factories import RecoleccionFactory, RecoleccionInput

TIPO_MAP = {
    "orgánico": "O",
    "inorgánico": "I",
    "peligroso": "P",
}

SUBCAT_MAP = {
    "fracción orgánica": "OR",
    "fracción vegetal": "VE",
    "residuos de poda": "PO",
}

MODALIDAD_MAP = {
    "programada": "PR",
    "bajo_de_manda": "BD",
}

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

@require_POST
def cerrar_sesion(request):
    request.session.flush()
    messages.info(request, 'Sesión cerrada.')
    return redirect('home')

def _get_current_usuario(request):
    """
    Intenta usar tu modelo Usuario guardado en sesión (como en tu proyecto),
    y si no, usa request.user (auth).
    """
    usuario_id = request.session.get("usuario_id")
    if usuario_id:
        try:
            return Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            pass
    # fallback si usas el user de Django
    try:
        return Usuario.objects.get(correo=request.user.email)  # ajusta si tu campo es distinto
    except Exception:
        return None

@login_required
@require_http_methods(["GET", "POST"])
def programar_recoleccion(request):
    if request.method == "POST":
        try:
            # 1) Normaliza entradas de formulario
            tipo_txt = (request.POST.get("tiporesiduo") or "").strip().lower()
            subcat_txt = (request.POST.get("subcategoria") or "").strip().lower()
            direccion = (request.POST.get("direccion") or "").strip()
            fecha_estimada = (request.POST.get("fechaestimada") or "").strip()
            cantidad_kg = (request.POST.get("cantidadkilos") or "").strip() or None
            modalidad_txt = (request.POST.get("modalidad") or "").strip().lower()
            comentario = (request.POST.get("comentarios") or "").strip()

            # 2) Mapear a codes de choices
            tipo = TIPO_MAP.get(tipo_txt)
            subcategoria = SUBCAT_MAP.get(subcat_txt)
            modalidad = MODALIDAD_MAP.get(modalidad_txt)

            if not all([tipo, subcategoria, direccion, fecha_estimada, modalidad]):
                messages.error(request, "Faltan datos o hay un valor inválido en el formulario.")
                return render(request, "request-collection.html")

            # 3) Usuario logueado
            usuario_id = request.session.get("usuario_id")
            usuario = Usuario.objects.get(id=usuario_id)

            # 4) Usa la Fábrica para obtener el servicio correcto
            service = RecoleccionFactory.for_tipo(tipo)

            # 5) Crea la recolección con la estrategia concreta
            entrada = RecoleccionInput(
                tipo_residuo=tipo,
                subcategoria=subcategoria,
                direccion=direccion,
                fecha_estimada=fecha_estimada,
                cantidad_kg=cantidad_kg,
                modalidad=modalidad,
                comentario=comentario,
                usuario=usuario,
            )
            recoleccion = service.crear_recoleccion(entrada)

            messages.success(
                request,
                f"Recolección #{recoleccion.id} creada y asignada a {recoleccion.empresa.nombre}."
            )
            return redirect("history")

        except IntegrityError:
            messages.error(request, "No se pudo crear la recolección por un conflicto de datos.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

    return render(request, "request-collection.html")

@login_required
def historial_recolecciones_usuario(request):
    usuario = _get_current_usuario(request)
    if not usuario:
        # Si algo falla, muestra vacío (o redirige a login/perfil)
        return render(request, "historial/historial_usuario.html", {
            "page_obj": [],
            "q": "",
            "order": "recientes",
        })

    q = (request.GET.get("q") or "").strip()
    order = (request.GET.get("order") or "recientes").lower()

    qs = (
        Recoleccion.objects.select_related("empresa", "usuario")
        .filter(usuario=usuario)
    )

    # Búsqueda simple (ajusta campos a gusto)
    if q:
        qs = qs.filter(
            Q(subcategoria__icontains=q)
            | Q(comentario__icontains=q)
            | Q(direccion__icontains=q)
            | Q(empresa__nombre__icontains=q)
        )

    # Ordenamiento
    if order == "recientes":
        qs = qs.order_by("-fecha_estimada", "-id")
    elif order == "antiguos":
        qs = qs.order_by("fecha_estimada", "id")
    elif order == "puntos_desc":
        # Si tienes campo puntos en el modelo, cámbialo por el nombre real.
        # Si no tienes, te muestro cómo estimarlo en el template.
        qs = qs.order_by("-puntos_acumulados", "-fecha_estimada") if hasattr(Recoleccion, "puntos_acumulados") else qs.order_by("-fecha_estimada", "-id")
    elif order == "puntos_asc":
        qs = qs.order_by("puntos_acumulados", "-fecha_estimada") if hasattr(Recoleccion, "puntos_acumulados") else qs.order_by("-fecha_estimada", "-id")
    else:
        qs = qs.order_by("-fecha_estimada", "-id")

    paginator = Paginator(qs, 10)  # 10 por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    ctx = {
        "page_obj": page_obj,
        "q": q,
        "order": order,
    }
    return render(request, "history_user.html", ctx)