from django.db import models
from personas.models import Login, Empleado


class Bitacora(models.Model):
    id_bitacora = models.AutoField(primary_key=True)
    id_login = models.ForeignKey(Login, on_delete=models.CASCADE)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    accion = models.TextField()
    detalle = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Bitácoras"

    def __str__(self):
        return f"Bitácora #{self.id_bitacora} - {self.fecha}"
