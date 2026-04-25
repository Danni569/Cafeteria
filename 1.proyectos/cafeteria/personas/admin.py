from django.contrib import admin
from .models import (
    Turno, EstadoCivil, Nacionalidad, Estado,
    TipoContacto, Salario, Empleado, Login, Cliente
)


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id_turno', 'descripcion')
    search_fields = ('descripcion',)


@admin.register(EstadoCivil)
class EstadoCivilAdmin(admin.ModelAdmin):
    list_display = ('id_estado_civil', 'descripcion')
    search_fields = ('descripcion',)


@admin.register(Nacionalidad)
class NacionalidadAdmin(admin.ModelAdmin):
    list_display = ('id_nacionalidad', 'descripcion')
    search_fields = ('descripcion',)


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id_estado', 'descripcion')
    search_fields = ('descripcion',)


@admin.register(TipoContacto)
class TipoContactoAdmin(admin.ModelAdmin):
    list_display = ('id_tipo_contacto', 'descripcion')
    search_fields = ('descripcion',)


@admin.register(Salario)
class SalarioAdmin(admin.ModelAdmin):
    list_display = ('id_salario', 'descripcion', 'monto')
    search_fields = ('descripcion',)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('id_empleado', 'nombre_empleado', 'ci', 'email', 'fecha_ingreso', 'pribilegios_como_adm', 'encargado')
    search_fields = ('nombre_empleado', 'ci', 'email')
    list_filter = ('id_turno', 'id_estado_civil', 'id_estado', 'fecha_ingreso', 'pribilegios_como_adm', 'encargado')
    readonly_fields = ('id_empleado',)
    fieldsets = (
        ('Información Personal', {
            'fields': ('id_empleado', 'nombre_empleado', 'ci', 'email', 'direccion')
        }),
        ('Contacto', {
            'fields': ('tel_fijo', 'cel', 'tel_contacto', 'nombre_contacto')
        }),
        ('Información Laboral', {
            'fields': ('fecha_ingreso', 'id_turno', 'id_salario')
        }),
        ('Datos Personales', {
            'fields': ('id_estado_civil', 'id_nacionalidad', 'id_estado')
        }),
        ('Permisos y Roles', {
            'fields': ('pribilegios_como_adm', 'encargado'),
            'description': 'Marcar si el empleado tiene privilegios especiales'
        }),
    )


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    list_display = ('id_login', 'nombre', 'email', 'estado', 'fecha_creacion')
    search_fields = ('nombre', 'email')
    list_filter = ('estado', 'fecha_creacion')
    readonly_fields = ('id_login', 'fecha_creacion', 'fecha_login')
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('id_empleado', 'nombre', 'email', 'password_hash', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_login')
        }),
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'nombre', 'ci_o_nit', 'fecha_registro')
    search_fields = ('nombre', 'ci_o_nit')
    list_filter = ('fecha_registro',)
    readonly_fields = ('id_cliente', 'fecha_registro')
    readonly_fields = ('id_cliente', 'fecha_registro')
    readonly_fields = ('id_cliente', 'fecha_registro')
