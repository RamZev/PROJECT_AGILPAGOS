# neumatic\apps\usuarios\views\user_password_views.py
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from apps.usuarios.forms.password_reset_form import CustomPasswordResetForm


class CustomPasswordResetView(PasswordResetView):
	"""
	Vista personalizada para solicitar recuperación de contraseña.
	Formatea el correo con HTML.
	"""
	form_class = CustomPasswordResetForm
	template_name = 'usuarios/password_reset_form.html'
	email_template_name = 'usuarios/password_reset_email.html'
	subject_template_name = 'usuarios/password_reset_subject.txt'
	success_url = reverse_lazy('password_reset_done')
	
	def form_valid(self, form):
		#-- Obtener el usuario validado por el formulario.
		user = form.cleaned_data.get('user')
		
		#-- Generar token y uid.
		token = default_token_generator.make_token(user)
		uid = urlsafe_base64_encode(force_bytes(user.pk))
		
		#-- Preparar contexto para el template.
		context = {
			'user': user,
			'protocol': 'https' if self.request.is_secure() else 'http',
			'domain': self.request.get_host(),
			'uid': uid,
			'token': token,
		}
		
		#-- Renderizar el template HTML del correo.
		html_message = render_to_string(self.email_template_name, context)
		
		#-- Crear versión texto plano.
		plain_message = strip_tags(html_message)
		
		#-- Renderizar el asunto.
		subject = render_to_string(self.subject_template_name, context)
		subject = ''.join(subject.splitlines())
		
		#-- Agregar prefijo si existe.
		if settings.EMAIL_SUBJECT_PREFIX:
			subject = f"{settings.EMAIL_SUBJECT_PREFIX}{subject}"
		
		#-- Crear y enviar el correo HTML.
		email_message = EmailMultiAlternatives(
			subject=subject,
			body=plain_message,
			from_email=None,  # Usa DEFAULT_FROM_EMAIL
			to=[user.email],
		)
		email_message.attach_alternative(html_message, "text/html")
		
		#-- Enviar con manejo de errores.
		try:
			email_message.send(fail_silently=False)
		except Exception as e:
			messages.error(
				self.request, 
				f'Error al enviar el correo: {str(e)}'
			)
			return redirect('password_reset')
		
		return redirect(self.success_url)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
	"""
	Vista personalizada para confirmar y establecer nueva contraseña
	"""
	template_name = 'usuarios/password_reset_confirm.html'
	success_url = reverse_lazy('password_reset_complete')
