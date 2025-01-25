from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'), 
    path('tasks/', views.tasks, name='tasks'),
    path('losmigration/', views.losmigration_view, name='losmigration'),
    path('create-user/', views.create_user, name='create_user'),
    path('success/', views.success, name='success'),
    path('sop-automation/', views.sopauomation, name='sopautomation'),
    path('get-tenants/', views.get_tenants, name='get-tenants'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

