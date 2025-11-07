# habilidades/views.py
from django.shortcuts import render

def index(request):
    # A página inicial será renderizada usando o template index.html
    return render(request, 'habilidades/index.html')    