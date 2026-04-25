"""
URL configuration for Mysitecoffe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from personas import views as personas_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', personas_views.login_view, name='login'),
    path('dashboard/', personas_views.dashboard_view, name='dashboard'),
    path('encargado/', personas_views.encargado_view, name='encargado'),
    path('inicio/', personas_views.inicio_view, name='inicio'),
    path('logout/', personas_views.logout_view, name='logout'),
    path('ventas/', personas_views.ver_ventas_view, name='ver_ventas'),
    path('cliente/crear/', personas_views.crear_cliente_view, name='crear_cliente'),
    path('cliente/obtener/', personas_views.obtener_clientes_json, name='obtener_clientes'),
    path('pedido/crear/', personas_views.crear_pedido_view, name='crear_pedido'),
    path('pedido/<int:pedido_id>/detalle/', personas_views.agregar_detalle_pedido_view, name='agregar_detalle_pedido'),
    path('pedido/<int:pedido_id>/nota-venta/', personas_views.nota_venta_view, name='nota_venta'),
    path('pedido/<int:pedido_id>/eliminar-detalle/<int:detalle_id>/', personas_views.eliminar_detalle_view, name='eliminar_detalle'),
    path('', personas_views.login_view, name='home'),
]
