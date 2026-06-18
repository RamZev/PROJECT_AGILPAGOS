# neumatic\apps\menu\context_processors.py
from apps.menu.models import MenuHeading, MenuItem

# En tu archivo context_processors.py - TEMPORAL
def menu_context(request):
    if not request.user.is_authenticated:
        return {}
    
    # print(f"DEBUG: Usuario: {request.user}, Superusuario: {request.user.is_superuser}")
    # print(f"DEBUG: Grupos del usuario: {[g.name for g in request.user.groups.all()]}")
    
    headings = MenuHeading.objects.all().order_by('order')
    menu_tree = {}
    
    for heading in headings:
        items = MenuItem.objects.filter(
            heading=heading, 
            parent=None
        ).prefetch_related('groups').order_by('order')
        
        visible_items = []
        
        for item in items:
            # VERIFICAR ACCESO CON VERIFICACIÓN RECURSIVA DE HIJOS
            has_access = item.has_access(request.user, check_children=True)
            # print(f"DEBUG: Item '{item.name}' - Grupos: {[g.name for g in item.groups.all()]} - is_collapse: {item.is_collapse} - Access: {has_access}")
            
            if not has_access:
                continue
                
            children_tree = build_menu_tree(item, request.user)
                
            visible_items.append({
                'item': item, 
                'children': children_tree
            })
        
        if visible_items:
            menu_tree[heading] = visible_items
    
    # print(f"DEBUG: Headings visibles: {[h.name for h in menu_tree.keys()]}")
    return {'menu_tree': menu_tree}


def build_menu_tree(menu_item, user):
    """
    Función recursiva para construir el árbol completo del menú
    con filtrado por permisos de usuario
    """
    children = MenuItem.objects.filter(parent=menu_item).order_by('order')
    children_tree = []
    
    for child in children:
        # VERIFICAR ACCESO DEL USUARIO AL HIJO (con verificación recursiva)
        if not child.has_access(user, check_children=True):
            continue
            
        grandchildren = build_menu_tree(child, user)
        
        children_tree.append({
            'item': child,
            'children': grandchildren
        })
    
    return children_tree