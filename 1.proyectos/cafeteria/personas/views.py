from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Login, Empleado, Cliente
from operaciones.models import Pedido, PedidoDetalle, NotaVenta
from menu.models import Producto
from categoria.models import CategoriaProducto
import json
from django.utils import timezone
from decimal import Decimal


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        # PRIMERO: Verificar si es administrador en auth_user
        try:
            auth_user = User.objects.get(email=email)
            
            # Verificar si es superuser
            if auth_user.is_superuser:
                # Intentar autenticar con Django
                user = authenticate(request, username=auth_user.username, password=password)
                
                if user is not None:
                    # Contraseña correcta y es superuser
                    from django.contrib.auth import login as django_login
                    django_login(request, user)
                    
                    # Guardar datos en sesión
                    request.session['user_email'] = email
                    request.session['user_nombre'] = auth_user.first_name or auth_user.username
                    request.session['user_is_admin'] = True
                    
                    messages.success(request, f'¡Bienvenido, Administrador!')
                    return redirect('/admin/')
                else:
                    messages.error(request, 'Email o contraseña incorrectos')
                    return render(request, 'personas/login.html')
        except User.DoesNotExist:
            # No es administrador, verificar si es empleado
            pass
        
        # SEGUNDO: Verificar si es empleado o encargado en tabla Login
        try:
            user = Login.objects.get(email=email)
            
            # Verificar si la cuenta está activa
            if not user.estado:
                messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
                return render(request, 'personas/login.html')
            
            # Verificar la contraseña (comparación simple de texto plano para pruebas)
            if user.password_hash == password:
                # Actualizar fecha de último login
                user.fecha_login = timezone.now()
                user.save()
                
                # Obtener el empleado asociado
                empleado = user.id_empleado
                
                # Guardar datos en sesión
                request.session['user_id'] = user.id_login
                request.session['user_email'] = user.email
                request.session['user_nombre'] = user.nombre
                request.session['user_is_admin'] = False
                request.session['empleado_id'] = empleado.id_empleado
                
                # Verificar si es encargado
                if empleado.encargado:
                    request.session['user_is_encargado'] = True
                    messages.success(request, f'¡Bienvenido, Encargado {user.nombre}!')
                    return redirect('encargado')
                else:
                    request.session['user_is_encargado'] = False
                    messages.success(request, f'¡Bienvenido, {user.nombre}!')
                    return redirect('dashboard')
            else:
                messages.error(request, 'Email o contraseña incorrectos')
        except Login.DoesNotExist:
            messages.error(request, 'Email o contraseña incorrectos')
    
    return render(request, 'personas/login.html')


def encargado_view(request):
    """Dashboard para encargados/supervisores con estadísticas y gráficos"""
    # Verificar que el usuario esté autenticado
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Verificar que sea encargado
    if not request.session.get('user_is_encargado', False):
        return redirect('dashboard')
    
    # Verificar que no sea administrador
    if request.session.get('user_is_admin', False):
        return redirect('/admin/')
    
    from django.utils import timezone
    from datetime import timedelta
    
    # Obtener la fecha de hoy
    hoy = timezone.now().date()
    
    # ESTADÍSTICAS DIARIAS
    ventas_hoy = NotaVenta.objects.filter(fecha=hoy)
    total_hoy = sum(nota.total for nota in ventas_hoy)
    meta_diaria = 1000
    cumple_meta = total_hoy >= meta_diaria
    
    # ESTADÍSTICAS TOTALES
    todas_las_ventas = NotaVenta.objects.all()
    total_dinero = sum(nota.total for nota in todas_las_ventas)
    total_transacciones = todas_las_ventas.count()
    
    # ÚLTIMAS 7 DÍAS (para gráficos)
    hace_7_dias = hoy - timedelta(days=6)
    ventas_7_dias = NotaVenta.objects.filter(fecha__gte=hace_7_dias).order_by('fecha')
    
    # Datos por día para el gráfico
    datos_por_dia = {}
    for i in range(7):
        fecha = hace_7_dias + timedelta(days=i)
        datos_por_dia[fecha.strftime('%d/%m')] = float(sum(
            nota.total for nota in ventas_7_dias.filter(fecha=fecha)
        ))
    
    # RANKING DE VENDEDORES
    vendedores = Empleado.objects.all()
    ranking_vendedores = []
    
    for empleado in vendedores:
        total_empleado = sum(
            nota.total for nota in NotaVenta.objects.filter(id_empleado=empleado)
        )
        cantidad_ventas = NotaVenta.objects.filter(id_empleado=empleado).count()
        if cantidad_ventas > 0:
            promedio = total_empleado / cantidad_ventas
            ranking_vendedores.append({
                'empleado': empleado,
                'total': float(total_empleado),
                'cantidad': cantidad_ventas,
                'promedio': float(promedio)
            })
    
    # Ordenar por total descendente
    ranking_vendedores.sort(key=lambda x: x['total'], reverse=True)
    
    # MÉTODOS DE PAGO
    metodos_pago_stats = {
        'efectivo': 0,
        'qr': 0,
        'tarjeta': 0
    }
    for nota in todas_las_ventas:
        if nota.metodo_pago in metodos_pago_stats:
            metodos_pago_stats[nota.metodo_pago] += float(nota.total)
    
    # Preparar datos para gráficos JSON
    import json
    datos_dias_json = json.dumps(list(datos_por_dia.values()))
    etiquetas_dias_json = json.dumps(list(datos_por_dia.keys()))
    datos_metodos_json = json.dumps(list(metodos_pago_stats.values()))
    
    context = {
        'user_nombre': request.session.get('user_nombre', 'Usuario'),
        'user_email': request.session.get('user_email', ''),
        # Datos diarios
        'total_hoy': float(total_hoy),
        'meta_diaria': meta_diaria,
        'cumple_meta': cumple_meta,
        'porcentaje_meta': min(int((float(total_hoy) / meta_diaria) * 100), 100) if meta_diaria > 0 else 0,
        # Datos totales
        'total_dinero': float(total_dinero),
        'total_transacciones': total_transacciones,
        'ventas_hoy_cantidad': ventas_hoy.count(),
        # Gráficos
        'datos_dias_json': datos_dias_json,
        'etiquetas_dias_json': etiquetas_dias_json,
        'datos_metodos_json': datos_metodos_json,
        # Ranking
        'ranking_vendedores': ranking_vendedores,
        'top_vendedor': ranking_vendedores[0] if ranking_vendedores else None,
        # Todas las ventas
        'todas_las_ventas': todas_las_ventas.order_by('-fecha', '-id_nota'),
    }
    return render(request, 'personas/encargado.html', context)


def dashboard_view(request):
    """Dashboard principal para empleados"""
    # Verificar que el usuario esté autenticado
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Verificar que sea empleado (no encargado ni admin)
    if request.session.get('user_is_encargado', False):
        return redirect('encargado')
    
    # Verificar que no sea administrador
    if request.session.get('user_is_admin', False):
        return redirect('/admin/')
    
    context = {
        'user_nombre': request.session.get('user_nombre', 'Usuario'),
        'user_email': request.session.get('user_email', ''),
    }
    return render(request, 'personas/dashboard.html', context)


@require_http_methods(["POST"])
def crear_cliente_view(request):
    """Vista para crear un cliente (vía AJAX)"""
    try:
        if 'user_id' not in request.session:
            return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
        
        nombre = request.POST.get('nombre', '').strip()
        ci_o_nit = request.POST.get('ci_o_nit', '').strip()
        
        # Validación básica
        if not nombre or not ci_o_nit:
            return JsonResponse({'success': False, 'error': 'Nombre y CI/NIT son requeridos'}, status=400)
        
        # Verificar si el cliente ya existe
        cliente_existente = Cliente.objects.filter(ci_o_nit=ci_o_nit).first()
        if cliente_existente:
            return JsonResponse({
                'success': True,
                'cliente_id': cliente_existente.id_cliente,
                'cliente_nombre': cliente_existente.nombre,
                'mensaje': 'Cliente ya existe'
            }, status=200)
        
        # Crear el nuevo cliente
        cliente = Cliente.objects.create(
            nombre=nombre,
            ci_o_nit=ci_o_nit
        )
        
        return JsonResponse({
            'success': True,
            'cliente_id': cliente.id_cliente,
            'cliente_nombre': cliente.nombre,
            'mensaje': f'Cliente {nombre} creado exitosamente'
        }, status=201)
    
    except Exception as e:
        import traceback
        print(f"Error al crear cliente: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def obtener_clientes_json(request):
    """Obtener lista de clientes en JSON"""
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    clientes = Cliente.objects.values('id_cliente', 'nombre', 'ci_o_nit').all()
    return JsonResponse(list(clientes), safe=False)


def crear_pedido_view(request):
    """Vista para crear un nuevo pedido"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id_empleado=empleado_id)
    
    if request.method == 'POST':
        # Crear el pedido
        pedido = Pedido.objects.create(
            id_cliente_id=request.POST.get('cliente'),
            id_empleado=empleado,
            total=Decimal('0')
        )
        
        # Redirigir a añadir detalles
        return redirect('agregar_detalle_pedido', pedido_id=pedido.id_pedido)
    
    # Obtener clientes
    clientes = Cliente.objects.all()
    
    context = {
        'user_nombre': request.session.get('user_nombre', 'Usuario'),
        'clientes': clientes,
    }
    return render(request, 'operaciones/crear_pedido.html', context)


def agregar_detalle_pedido_view(request, pedido_id):
    """Vista para agregar detalles al pedido"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        # Verificar si es AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            producto_id = request.POST.get('producto', '').strip()
            cantidad_str = request.POST.get('cantidad', '1').strip()
            
            # Validar que los parámetros no estén vacíos
            if not producto_id:
                error_msg = 'El producto es requerido'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('agregar_detalle_pedido', pedido_id=pedido_id)
            
            # Validar cantidad
            try:
                cantidad = int(cantidad_str)
                if cantidad < 1:
                    raise ValueError()
            except (ValueError, TypeError):
                error_msg = 'La cantidad debe ser un número mayor a 0'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('agregar_detalle_pedido', pedido_id=pedido_id)
            
            # Validar que el producto exista
            try:
                producto = Producto.objects.get(id_producto=producto_id)
            except Producto.DoesNotExist:
                error_msg = 'El producto no existe'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=404)
                messages.error(request, error_msg)
                return redirect('agregar_detalle_pedido', pedido_id=pedido_id)
            
            # Calcular precios
            precio_unitario = producto.precio
            subtotal = precio_unitario * cantidad
            
            # Crear detalle del pedido
            detalle = PedidoDetalle.objects.create(
                id_pedido=pedido,
                id_producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
            
            # Actualizar total del pedido
            total = sum(d.subtotal for d in PedidoDetalle.objects.filter(id_pedido=pedido))
            pedido.total = total
            pedido.save()
            
            success_msg = f'{producto.nombre} agregado al pedido'
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'detalle_id': detalle.id_detalle,
                    'producto_nombre': producto.nombre,
                    'precio_unitario': str(precio_unitario),
                    'cantidad': cantidad,
                    'subtotal': str(subtotal),
                    'total_pedido': str(pedido.total),
                    'mensaje': success_msg
                }, status=201)
            
            messages.success(request, success_msg)
            return redirect('agregar_detalle_pedido', pedido_id=pedido_id)
            
        except Exception as e:
            import traceback
            print(f"Error al agregar detalle: {str(e)}")
            print(traceback.format_exc())
            error_msg = f'Error al agregar producto: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=500)
            messages.error(request, error_msg)
            return redirect('agregar_detalle_pedido', pedido_id=pedido_id)
    
    # GET - Mostrar formulario
    productos = Producto.objects.filter(disponible=True).order_by('nombre')
    detalles = PedidoDetalle.objects.filter(id_pedido=pedido).select_related('id_producto')
    
    context = {
        'user_nombre': request.session.get('user_nombre', 'Usuario'),
        'pedido': pedido,
        'productos': productos,
        'detalles': detalles,
    }
    return render(request, 'operaciones/agregar_detalle.html', context)


def nota_venta_view(request, pedido_id):
    """Vista para mostrar la nota de venta"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        # Obtener método de pago
        metodo_pago = request.POST.get('metodo_pago', 'efectivo')
        
        # Actualizar estado del pedido a entregado
        pedido.estado = 'entregado'
        pedido.save()
        
        # Crear o actualizar la nota de venta
        nota, created = NotaVenta.objects.update_or_create(
            id_pedido=pedido,
            defaults={
                'id_cliente': pedido.id_cliente,
                'id_empleado': pedido.id_empleado,
                'total': pedido.total,
                'metodo_pago': metodo_pago
            }
        )
        
        messages.success(request, 'Nota de venta generada exitosamente')
    
    # Obtener o crear la nota de venta
    nota, created = NotaVenta.objects.get_or_create(
        id_pedido=pedido,
        defaults={
            'id_cliente': pedido.id_cliente,
            'id_empleado': pedido.id_empleado,
            'total': pedido.total,
            'metodo_pago': 'efectivo'
        }
    )
    
    detalles = PedidoDetalle.objects.filter(id_pedido=pedido)
    
    # Obtener enum de métodos de pago
    from operaciones.models import MetodoPagoEnum
    metodos_pago = MetodoPagoEnum.choices
    
    context = {
        'user_nombre': request.session.get('user_nombre', 'Usuario'),
        'nota': nota,
        'pedido': pedido,
        'detalles': detalles,
        'metodos_pago': metodos_pago,
    }
    return render(request, 'operaciones/nota_venta.html', context)


def eliminar_detalle_view(request, pedido_id, detalle_id):
    """Eliminar un detalle del pedido"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    detalle = get_object_or_404(PedidoDetalle, id_detalle=detalle_id)
    pedido = detalle.id_pedido
    
    detalle.delete()
    
    # Actualizar total
    total = sum(d.subtotal for d in PedidoDetalle.objects.filter(id_pedido=pedido))
    pedido.total = total
    pedido.save()
    
    # Verificar si es AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_ajax:
        return JsonResponse({'success': True, 'total': str(pedido.total)})
    
    messages.success(request, 'Detalle eliminado')
    return redirect('agregar_detalle_pedido', pedido_id=pedido_id)


def inicio_view(request):
    # Verificar que el usuario esté autenticado
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Verificar que no sea administrador
    if request.session.get('user_is_admin', False):
        return redirect('/admin/')
    
    context = {
        'user_nombre': request.session.get('user_nombre', 'Usuario'),
    }
    return render(request, 'personas/inicio.html', context)


def logout_view(request):
    """Cerrar sesión del usuario"""
    from django.contrib.auth import logout as django_logout
    
    # Limpiar la sesión de Django
    django_logout(request)
    
    # Limpiar la sesión personalizada
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('login')


def ver_ventas_view(request):
    """Vista para mostrar todas las ventas del empleado autenticado"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Verificar que sea empleado (no encargado ni admin)
    if request.session.get('user_is_encargado', False):
        return redirect('encargado')
    
    if request.session.get('user_is_admin', False):
        return redirect('/admin/')
    
    # Obtener el ID del empleado autenticado
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id_empleado=empleado_id)
    
    # Obtener todas las notas de venta del empleado
    notas_venta = NotaVenta.objects.filter(id_empleado=empleado).order_by('-fecha')
    
    # Calcular estadísticas
    total_ventas = notas_venta.count()
    total_monto = sum(nota.total for nota in notas_venta)
    
    context = {
        'user_nombre': request.session.get('user_nombre', 'Usuario'),
        'notas_venta': notas_venta,
        'total_ventas': total_ventas,
        'total_monto': total_monto,
        'empleado': empleado,
    }
    return render(request, 'personas/ver_ventas.html', context)
