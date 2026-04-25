from django.shortcuts import redirect
from django.contrib.auth.models import User


class AdminProtectionMiddleware:
    """Middleware para proteger el panel de administración"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si intenta acceder a /admin/
        if request.path.startswith('/admin/'):
            # Permitir acceso al login de admin y a recursos estáticos
            if request.path in ['/admin/login/', '/admin/']:
                # Verificar si el usuario está autenticado y es superuser
                if not request.user.is_authenticated:
                    # Redirigir al login de empleado
                    return redirect('/login/')
                elif not request.user.is_superuser:
                    # No es superuser, redirigir al login de empleado
                    return redirect('/login/')
            elif request.path.startswith('/admin/'):
                # Verificar autenticación para cualquier otra ruta de admin
                if not request.user.is_authenticated or not request.user.is_superuser:
                    # No está autenticado o no es superuser
                    return redirect('/login/')
        
        response = self.get_response(request)
        return response
