from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            login_url = f"{reverse('signup')}?next={request.get_full_path()}"
            return redirect(login_url)
        return view_func(request, *args, **kwargs)
    return _wrapped
