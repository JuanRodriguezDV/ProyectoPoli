from django.db import models

# Create your models here.
class Usuario(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    documento = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    nombre_usuario = models.CharField(max_length=100, unique=True)
    fecha_nacimiento = models.DateField()
    correo = models.EmailField(unique=True)
    celular = models.CharField(max_length=15, unique=True)
    contrasena = models.CharField(max_length=128)
    direccion = models.CharField(max_length=255)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)

class EmpresaRecolectora(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

class Recoleccion(models.Model):
    TIPO_RESIDUO_CHOICES = [
        ('O', 'Orgánico'),
        ('I', 'Inorgánico'),
        ('P', 'Peligroso'),
    ]
    SUBCATEGORIA_CHOICES = [
        ('OR', 'Orgánica'),
        ('VE', 'Vegetal'),
        ('PO', 'Poda'),
    ]
    MODALIDAD_CHOICES = [
        ('PR', 'Programada'),
        ('BD', 'Baja demanda'),
    ]
    tipo_residuo = models.CharField(max_length=1, choices=TIPO_RESIDUO_CHOICES)
    subcategoria = models.CharField(max_length=2, choices=SUBCATEGORIA_CHOICES)
    direccion = models.CharField(max_length=255)
    fecha_estimada = models.DateField()
    cantidad_kg = models.DecimalField(max_digits=7, decimal_places=2)
    modalidad_recoleccion = models.CharField(max_length=2, choices=MODALIDAD_CHOICES)
    comentario = models.TextField(blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    empresa = models.ForeignKey(EmpresaRecolectora, on_delete=models.CASCADE)