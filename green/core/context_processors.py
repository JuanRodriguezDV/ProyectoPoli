from .models import Usuario

def usuario_context(request):
    uid = request.session.get('usuario_id')
    usuario = None
    if uid:
        try:
            usuario = Usuario.objects.get(id=uid)
        except Usuario.DoesNotExist:
            pass
    return {'usuario_actual': usuario}
