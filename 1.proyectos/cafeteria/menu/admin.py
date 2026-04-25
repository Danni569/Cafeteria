from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre', 'id_categoria', 'precio', 'disponible')
    search_fields = ('nombre',)
    list_filter = ('disponible', 'id_categoria')
    readonly_fields = ('id_producto',)
