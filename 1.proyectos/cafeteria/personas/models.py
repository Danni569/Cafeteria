from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.hashers import make_password, check_password


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Turnos"

    def __str__(self):
        return self.descripcion


class EstadoCivil(models.Model):
    id_estado_civil = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Estados Civiles"

    def __str__(self):
        return self.descripcion


class Nacionalidad(models.Model):
    id_nacionalidad = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Nacionalidades"

    def __str__(self):
        return self.descripcion


class Estado(models.Model):
    id_estado = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Estados"

    def __str__(self):
        return self.descripcion


class TipoContacto(models.Model):
    id_tipo_contacto = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Tipos de Contacto"

    def __str__(self):
        return self.descripcion


class Salario(models.Model):
    id_salario = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=150)
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name_plural = "Salarios"

    def __str__(self):
        return self.descripcion


class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombre_empleado = models.CharField(max_length=200)
    ci = models.CharField(max_length=20, unique=True, blank=True, null=True)
    tel_fijo = models.CharField(max_length=20, blank=True, null=True)
    cel = models.CharField(max_length=20, blank=True, null=True)
    tel_contacto = models.CharField(max_length=20, blank=True, null=True)
    nombre_contacto = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=200, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_ingreso = models.DateField()
    id_turno = models.ForeignKey(Turno, on_delete=models.RESTRICT, blank=True, null=True)
    id_estado_civil = models.ForeignKey(EstadoCivil, on_delete=models.RESTRICT, blank=True, null=True)
    id_nacionalidad = models.ForeignKey(Nacionalidad, on_delete=models.RESTRICT, blank=True, null=True)
    id_estado = models.ForeignKey(Estado, on_delete=models.RESTRICT, blank=True, null=True)
    id_tipo_contacto = models.ForeignKey(TipoContacto, on_delete=models.RESTRICT, blank=True, null=True)
    id_salario = models.ForeignKey(Salario, on_delete=models.RESTRICT, blank=True, null=True)
    pribilegios_como_adm = models.BooleanField(default=False)
    encargado = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Empleados"

    def __str__(self):
        return self.nombre_empleado


class Login(models.Model):
    id_login = models.AutoField(primary_key=True)
    id_empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    password_hash = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Logins"

    def set_password(self, raw_password):
        """Encripta la contraseña usando el algoritmo de Django"""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica si la contraseña coincide con el hash almacenado"""
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    ci_o_nit = models.CharField(max_length=20, blank=True, null=True)
    nombre = models.CharField(max_length=200)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nombre
