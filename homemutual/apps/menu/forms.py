from django import forms
from django.contrib.auth.models import Group
from django.db.models import Case, When, Max
from .models import MenuHeading, MenuItem


class MenuHeadingForm(forms.ModelForm):
    class Meta:
        model = MenuHeading
        fields = ['name', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nombre del Encabezado',
            'order': 'Orden de Aparición',
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            'heading', 'parent', 'name', 'url_name', 
            'query_params', 'icon', 'is_collapse', 'order', 'groups'
        ]
        widgets = {
            'heading': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre_url'}),
            'query_params': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '?parametro=valor'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-home'}),
            'is_collapse': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            # CheckboxSelectMultiple SIN attrs conflictivos
            'groups': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Función para mostrar la ruta jerárquica completa
        def get_hierarchical_label(obj):
            path_parts = [obj.name]
            current = obj
            
            # Construir la ruta desde el item hasta el heading
            while current.parent:
                path_parts.insert(0, current.parent.name)
                current = current.parent
            
            # SIEMPRE agregar el heading al principio
            if obj.heading:
                path_parts.insert(0, obj.heading.name)
            else:
                # Si no tiene heading, buscar el heading del padre
                if obj.parent and obj.parent.heading:
                    path_parts.insert(0, obj.parent.heading.name)
            
            return " → ".join(path_parts)
        
        self.fields['parent'].label_from_instance = get_hierarchical_label
        
        # Obtener solo items colapsables en el orden del árbol
        def get_collapsable_items_ordered():
            headings = MenuHeading.objects.order_by('order')
            collapsable_items = []
            
            for heading in headings:
                # Items de nivel 1 (sin parent) que son colapsables
                level1_items = MenuItem.objects.filter(
                    heading=heading, 
                    parent=None,
                    is_collapse=True
                ).order_by('order')
                
                for level1_item in level1_items:
                    collapsable_items.append(level1_item)
                    
                    # Items de nivel 2 (hijos) que son colapsables
                    level2_items = level1_item.children.filter(
                        is_collapse=True
                    ).order_by('order')
                    
                    for level2_item in level2_items:
                        collapsable_items.append(level2_item)
                        
                        # Items de nivel 3 (nietos) que son colapsables
                        level3_items = level2_item.children.filter(
                            is_collapse=True
                        ).order_by('order')
                        
                        for level3_item in level3_items:
                            collapsable_items.append(level3_item)
            
            return collapsable_items
        
        # Filtrar items padres para evitar referencias circulares
        collapsable_items = get_collapsable_items_ordered()
        
        # Crear una lista de IDs en el orden correcto
        ordered_ids = [item.pk for item in collapsable_items]
        
        if self.instance.pk:
            # Excluir el item actual y mantener el orden
            ordered_ids = [pk for pk in ordered_ids if pk != self.instance.pk]
        
        # Forzar el orden usando la lista de IDs
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)])
        
        queryset = MenuItem.objects.filter(pk__in=ordered_ids).order_by(preserved_order)
        
        self.fields['parent'].queryset = queryset
        
        # CONFIGURACIÓN DEL CAMPO GROUPS (SIMPLIFICADA)
        self.fields['groups'].help_text = 'Seleccione los grupos que pueden ver este item. Si no selecciona ninguno, solo los superusuarios podrán verlo.'
        self.fields['groups'].required = False
        
        # Ordenar los grupos por nombre para mejor usabilidad
        self.fields['groups'].queryset = Group.objects.order_by('name')
        
        # Debug
        print(f"Items colapsables disponibles: {queryset.count()}")
        for item in queryset:
            print(f" - {get_hierarchical_label(item)}")