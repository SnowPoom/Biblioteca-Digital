from .models import Notificacion

def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
