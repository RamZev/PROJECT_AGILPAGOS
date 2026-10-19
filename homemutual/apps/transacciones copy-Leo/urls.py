# apps/transacciones/urls.py
from django.urls import path
from .views.transferencia_views import *


urlpatterns = [
    path('transferencia/', TransferenciaListView.as_view(), name='transferencia_list'),
    path('transferencia/nueva/', TransferenciaCreateView.as_view(), name='transferencia_create'),
    path('transferencia/<int:pk>/editar/', TransferenciaUpdateView.as_view(), name='transferencia_update'),
    path('transferencia/<int:pk>/eliminar/', TransferenciaDeleteView.as_view(), name='transferencia_delete'),
]