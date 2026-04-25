from django.db import models
from django.core.validators import MinValueValidator
from menu.models import Producto
from personas.models import Cliente, Empleado


class EstadoPedidoEnum(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    EN_PREPARACION = 'en_preparacion', 'En preparación'
    LISTO = 'listo', 'Listo'
    ENTREGADO = 'entregado', 'Entregado'
    CANCELADO = 'cancelado', 'Cancelado'


class MetodoPagoEnum(models.TextChoices):
    EFECTIVO = 'efectivo', 'Efectivo'
    QR = 'qr', 'QR'
    TARJETA = 'tarjeta', 'Tarjeta'


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoPedidoEnum.choices,
        default=EstadoPedidoEnum.PENDIENTE
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id_pedido}"


class PedidoDetalle(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.RESTRICT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name_plural = "Detalles de Pedido"

    def __str__(self):
        return f"Detalle #{self.id_detalle} - Pedido #{self.id_pedido.id_pedido}"


class NotaVenta(models.Model):
    id_nota = models.AutoField(primary_key=True)
    id_pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT)
    fecha = models.DateField(auto_now_add=True)
    nit = models.CharField(max_length=20, blank=True, null=True)
    razon_social = models.CharField(max_length=300, blank=True, null=True)
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPagoEnum.choices
    )

    class Meta:
        verbose_name_plural = "Notas de Venta"

    def __str__(self):
        return f"Nota #{self.id_nota}"
