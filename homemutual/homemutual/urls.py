from django.contrib import admin
from django.urls import path, include
from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('usuarios/', include('apps.usuarios.urls')),
    path('maestros/', include('apps.maestros.urls')),
    path('menu/', include('apps.menu.urls')),
]
