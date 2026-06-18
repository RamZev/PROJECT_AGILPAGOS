# neumatic\apps\usuarios\views\user_password_views.py
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from apps.usuarios.forms.password_reset_form import CustomPasswordResetForm


class CustomPasswordResetView(PasswordResetView):
	"""
	Vista personalizada para solicitar recuperación de contraseña.
	Requiere email Y username para identificar al usuario.
	El cuerpo del correo se envía en formato de texto plano.
	"""
	form_class = CustomPasswordResetForm
	template_name = 'usuarios/password_reset_form.html'
	email_template_name = 'usuarios/password_reset_email.txt'
	subject_template_name = 'usuarios/password_reset_subject.txt'
	success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
	"""
	Vista personalizada para confirmar y establecer nueva contraseña
	"""
	template_name = 'usuarios/password_reset_confirm.html'
	success_url = reverse_lazy('password_reset_complete')
