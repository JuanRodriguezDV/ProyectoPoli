from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home (request):
    return render(request, 'home.html')

#inicio de sesion
def signin (request):
    return render(request, 'signin.html')

#crear cuenta
def signup (request):
    return render(request, 'signup.html')

#Solucitud de recoleccion de residuos
def requestcollection (requestcollection):
    return render(requestcollection, 'requestcollection.html')