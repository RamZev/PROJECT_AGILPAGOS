# apps/consultas/urls.py
from django.urls import path
from .views import consulta_cvu_views

urlpatterns = [
    # path('', consulta_cvu_views.ConsultaCvuPorCuitView.as_view(), name='consulta_cvu_por_cuit'),
    path('cvu-por-cuit/', consulta_cvu_views.ConsultaCvuPorCuitView.as_view(), name='consulta_cvu_por_cuit'),
]