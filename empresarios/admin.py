from django.contrib import admin
from .models import Empresas, Documento, Metricas

# Registrar os Models

admin.site.register(Empresas)
admin.site.register(Documento)
admin.site.register(Metricas)
