"""
URL configuration for green project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.pagina_de_inicio, name='home'),
    path('signin', views.iniciar_sesion, name='signin'),
    path('signup', views.crear_cuenta, name='signup'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('request-collection', views.programar_recoleccion, name='request-collection'),
    path('history', views.historial_recolecciones_usuario, name='history'),
    path('admin/', admin.site.urls),
]
