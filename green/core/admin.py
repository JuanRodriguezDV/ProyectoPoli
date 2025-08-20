from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Usuario, EmpresaRecolectora, Recoleccion

admin.site.register(Usuario)
admin.site.register(EmpresaRecolectora)
admin.site.register(Recoleccion)
