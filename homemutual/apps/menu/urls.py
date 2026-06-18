# neumatic\apps\menu\urls.py
from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Mantenimiento de MenuHeadings
    path('headings/', views.MenuHeadingListView.as_view(), name='heading_list'),
    path('headings/crear/', views.MenuHeadingCreateView.as_view(), name='heading_create'),
    path('headings/editar/<int:pk>/', views.MenuHeadingUpdateView.as_view(), name='heading_update'),
    path('headings/eliminar/<int:pk>/', views.MenuHeadingDeleteView.as_view(), name='heading_delete'),
    
    # Mantenimiento de MenuItems
    path('items/', views.MenuItemListView.as_view(), name='item_list'),
    path('items/crear/', views.MenuItemCreateView.as_view(), name='item_create'),
    path('items/editar/<int:pk>/', views.MenuItemUpdateView.as_view(), name='item_update'),
    path('items/eliminar/<int:pk>/', views.MenuItemDeleteView.as_view(), name='item_delete'),
    
    # Vista para gestionar árbol completo
    path('arbol/', views.MenuTreeView.as_view(), name='menu_tree'),

    path('get-children-count/', views.GetChildrenCountView.as_view(), name='get_children_count'),
]