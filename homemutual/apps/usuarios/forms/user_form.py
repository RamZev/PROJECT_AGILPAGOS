# neumatic\apps\usuarios\forms\user_form.py
from django import forms

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

#from apps.usuarios.models.user_models import User
from apps.usuarios.models import User

from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclasscheck)


class RegistroUsuarioForm(UserCreationForm):
	
	password1 = forms.CharField(
		label="Contraseña",
		widget=forms.PasswordInput(attrs={**formclasstext})
	)
	password2 = forms.CharField(
		label="Confirmar Contraseña",
		widget=forms.PasswordInput(attrs={**formclasstext})
	)
	
	class Meta:
		model = User
		fields = [
			'username',
			'first_name',
			'last_name',
			'email',
			'telefono',
			'is_active',
			'is_staff',
			'password1',
			'password2',
		]
		
		widgets = {
			'username': 
				forms.TextInput(attrs={**formclasstext}),
			'first_name': 
				forms.TextInput(attrs={**formclasstext}),
			'last_name': 
				forms.TextInput(attrs={**formclasstext}),
			'email': 
				forms.EmailInput(attrs={**formclasstext}),
			'telefono': 
				forms.TextInput(attrs={**formclasstext}),
			'is_active': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'is_staff': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}


class EditarUsuarioForm(UserChangeForm):
	
	class Meta:
		model = User
		fields = [
			'username',
			'first_name',
			'last_name',
			'email',
			'telefono',
			'is_active',
			'is_staff',
		]
		
		widgets = {
			'username': 
				forms.TextInput(attrs={**formclasstext}),
			'first_name': 
				forms.TextInput(attrs={**formclasstext}),
			'last_name': 
				forms.TextInput(attrs={**formclasstext}),
			'email': 
				forms.TextInput(attrs={**formclasstext}),
			'telefono': 
				forms.TextInput(attrs={**formclasstext}),
			'is_active': 
				forms.CheckboxInput(attrs={**formclasscheck}),
			'is_staff': 
				forms.CheckboxInput(attrs={**formclasscheck}),
		}


class GroupForm(forms.ModelForm):
	class Meta:
		model = Group
		fields = ["name"]
