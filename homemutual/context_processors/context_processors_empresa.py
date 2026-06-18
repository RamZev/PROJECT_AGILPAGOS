# neumatic\apps\menu\context_empresa.py
from apps.maestros.models.empresa_models import Empresa

def empresa_context(request):
    if not request.user.is_authenticated:
        return {}
    
    empresa = Empresa.objects.first()

    return {'empresa': empresa}


