from django.contrib import admin
from .models import CategoriaProducto


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre', 'descripcion')
    search_fields = ('nombre',)
    list_filter = ('nombre',)
