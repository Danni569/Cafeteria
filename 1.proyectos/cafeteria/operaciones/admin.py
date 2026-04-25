from django.contrib import admin
from .models import Pedido, PedidoDetalle, NotaVenta


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'id_cliente', 'id_empleado', 'fecha', 'estado', 'total')
    search_fields = ('id_cliente__nombre',)
    list_filter = ('estado', 'fecha')
    readonly_fields = ('id_pedido', 'fecha')


@admin.register(PedidoDetalle)
class PedidoDetalleAdmin(admin.ModelAdmin):
    list_display = ('id_detalle', 'id_pedido', 'id_producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('id_pedido__id_pedido',)
    list_filter = ('id_pedido',)
    readonly_fields = ('id_detalle',)


@admin.register(NotaVenta)
class NotaVentaAdmin(admin.ModelAdmin):
    list_display = ('id_nota', 'id_pedido', 'id_cliente', 'fecha', 'metodo_pago', 'total')
    search_fields = ('nit', 'razon_social')
    list_filter = ('metodo_pago', 'fecha')
    readonly_fields = ('id_nota', 'fecha')
