# apps/consultas/views/consulta_cvu_views.py
import logging

from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages

from apps.core.mixins import StaffRequiredMixin
from apps.maestros.services.agilpagos_client import (
    agilpagos_get,
    CredentialsNotInSession,
)

from ..forms.consulta_cvu_forms import ConsultaCvuPorCuitForm

logger = logging.getLogger(__name__)


class ConsultaCvuPorCuitView(StaffRequiredMixin, FormView):
    """
    Consulta las CVUs de un usuario en Agilpagos por su CUIT.
    Endpoint Agilpagos: GET /onboarding/usuario/consulta/{cuit}
    """
    template_name = 'consultas/cvu_por_cuit.html'
    form_class = ConsultaCvuPorCuitForm
    success_url = reverse_lazy('consulta_cvu_por_cuit')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resultado'] = self.request.session.pop('consulta_resultado', None)
        return context

    def form_valid(self, form):
        cuit = form.cleaned_data['cuit']
        resultado = {
            'cuit': cuit,
            'existe': False,
            'id_usuario': None,
            'cuentas': [],
            'error': None,
            'status_code': None,
        }

        try:
            response = agilpagos_get(
                self.request,
                f"/onboarding/usuario/consulta/{cuit}"
            )
        except CredentialsNotInSession:
            messages.error(
                self.request,
                '❌ Sesión sin credenciales de Agilpagos. Vuelva a iniciar sesión.'
            )
            return self.form_invalid(form)
        except Exception as e:
            logger.exception("Error consultando Agilpagos")
            messages.error(self.request, f'❌ Error de conexión con Agilpagos: {e}')
            return self.form_invalid(form)

        resultado['status_code'] = response.status_code

        # Caso 1: el usuario existe (200)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {}
            resultado['existe'] = True
            usuarios = data.get('usuario', [])
            resultado['id_usuario'] = usuarios[0] if usuarios else None
            resultado['cuentas'] = data.get('cuentas', [])
            messages.success(
                self.request,
                f"✅ Usuario encontrado. {len(resultado['cuentas'])} CVU(s)."
            )

        # Caso 2: el usuario no existe (500 + "no encontrado")
        elif response.status_code == 500:
            try:
                detail = response.json().get('detail', '')
            except Exception:
                detail = response.text
            if 'no encontrado' in detail.lower():
                resultado['existe'] = False
                messages.warning(
                    self.request,
                    f"⚠️ El CUIT {cuit} no está registrado en Agilpagos."
                )
            else:
                resultado['error'] = detail
                messages.error(
                    self.request,
                    f'❌ Agilpagos respondió 500: {detail}'
                )

        # Caso 3: otros errores
        else:
            try:
                detalle = response.json()
            except Exception:
                detalle = response.text
            resultado['error'] = str(detalle)
            messages.error(
                self.request,
                f'❌ Agilpagos respondió {response.status_code}: {detalle}'
            )

        # Guardar el resultado en la sesión para mostrarlo después del redirect
        self.request.session['consulta_resultado'] = resultado

        return super().form_valid(form)