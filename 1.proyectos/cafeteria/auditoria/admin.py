from django.contrib import admin
from .models import Bitacora


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('id_bitacora', 'id_login', 'id_empleado', 'fecha', 'accion')
    search_fields = ('id_empleado__nombre_empleado', 'accion')
    list_filter = ('fecha',)
    readonly_fields = ('id_bitacora', 'fecha')
