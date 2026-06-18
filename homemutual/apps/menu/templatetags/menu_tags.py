from django import template
from ..models import MenuHeading, MenuItem

register = template.Library()

@register.inclusion_tag('menu/partials/dynamic_sidebar.html')
def render_menu(user):
    headings = MenuHeading.objects.all()
    menu_tree = {}
    for heading in headings:
        items = MenuItem.objects.filter(heading=heading, parent=None)
        visible_items = build_visible_tree(items, user)
        if visible_items:
            menu_tree[heading] = visible_items
    return {'menu_tree': menu_tree}

def build_visible_tree(items, user, level=0):
    visible = []
    for item in items.order_by('order'):
        if item.has_access(user):
            children = build_visible_tree(item.children.all(), user, level + 1)
            if item.is_collapse and not children:
                continue
            visible.append({
                'item': item,
                'children': children,
                'level': level,
            })
    return visible