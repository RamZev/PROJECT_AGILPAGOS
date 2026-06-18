# neumatic\apps\usuarios\forms\password_reset_form.py
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomPasswordResetForm(PasswordResetForm):
	"""
	Formulario personalizado que requiere email Y username
	"""
	username = forms.CharField(
		label="Nombre de Usuario",
		max_length=150,
		required=True,
		error_messages={
			'required': 'El nombre de usuario es obligatorio.',
			'max_length': 'El nombre de usuario no puede tener más de 150 caracteres.',
		},
		widget=forms.TextInput(attrs={
			'class': 'form-control',
			'placeholder': 'Ingresa tu nombre de usuario',
			'autocomplete': 'username'
		})
	)
	
	email = forms.EmailField(
		label="Correo Electrónico",
		required=True,
		error_messages={
			'required': 'El correo electrónico es obligatorio.',
			'invalid': 'Ingresa un correo electrónico válido (ejemplo: usuario@dominio.com).',
		},
		widget=forms.EmailInput(attrs={
			'class': 'form-control',
			'placeholder': 'usuario@ejemplo.com',
			'autocomplete': 'email'
		})
	)
	
	def clean(self):
		cleaned_data = super().clean()
		email = cleaned_data.get('email')
		username = cleaned_data.get('username')
		
		#-- Si alguno de los campos está vacío, salimos (los errores ya fueron agregados por Django).
		if not username or not email:
			return cleaned_data
		
		#-- Buscar usuario que coincida con ambos campos.
		try:
			user = User.objects.get(email=email, username=username)
			cleaned_data['user'] = user
			
			#-- Verificar si el usuario está activo.
			if not user.is_active:
				self.add_error(None, 'Tu cuenta está desactivada. Por favor, contacta al administrador.')
				
		except User.DoesNotExist:
			#-- Verificar si existe el email pero no el username, o viceversa.
			email_exists = User.objects.filter(email=email).exists()
			username_exists = User.objects.filter(username=username).exists()
			
			if email_exists and not username_exists:
				self.add_error('username', f'El nombre de usuario "{username}" no está asociado al correo {email}. Verifica tu nombre de usuario.')
			elif not email_exists and username_exists:
				self.add_error('email', f'El correo electrónico {email} no está asociado al usuario "{username}". Verifica tu correo electrónico.')
			else:
				self.add_error(None, 'No existe una cuenta con ese correo electrónico y nombre de usuario. Por favor, verifica tus datos.')
		
		return cleaned_data
	
	def get_users(self, email):
		"""
		Override del método para que use el usuario validado
		"""
		if hasattr(self, 'cleaned_data') and 'user' in self.cleaned_data:
			return [self.cleaned_data['user']]
		return super().get_users(email)