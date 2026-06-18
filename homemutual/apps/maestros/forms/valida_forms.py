# neumatic\apps\maestros\forms\valida_forms.py
from django import forms
from django.db.models import Q 
from datetime import time


from .crud_forms_generics import CrudGenericForm
from models.valida_models import Valida
from diseno_base.diseno_bootstrap import (
	formclasstext, formclassselect, formclassdate)


class ValidaForm(CrudGenericForm):
	
	class Meta:
		model = Valida
		fields = '__all__'

		widgets = {
			'estatus_valida': 
				forms.Select(attrs={**formclassselect}), 
			'id_sucursal': 
				forms.Select(attrs={**formclassselect}),
			'fecha_valida':
				forms.TextInput(attrs={**formclassdate, 'type': 'date', 'readonly': 'readonly'}),
			'hora_valida':
				forms.TimeInput(attrs={**formclasstext, 'readonly': 'readonly'}),
			'solicitado': 
				forms.TextInput(attrs={**formclasstext}),				
			'comentario':
				forms.TextInput(attrs={**formclasstext}),
			'id_cliente': 
				forms.Select(attrs={**formclassselect}), 
			'compro': 
				forms.Select(attrs={**formclassselect}), 
			'numero_comprobante':
				forms.TextInput(attrs={**formclasstext}),
			'hs':
				forms.TextInput(attrs={**formclasstext, 'readonly': 'readonly'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['hora_valida'].input_formats = ['%H:%M']
		self.fields['hs'].input_formats = ['%H:%M']
  
		# Filtra los últimos 50 clientes (por id descendente)
		# self.fields['id_cliente'].queryset = Cliente.objects.order_by('-id_cliente')[:50]
		self.fields['id_cliente'].queryset = Cliente.objects.filter(
				Q(id_cliente=114384)
		).order_by('-nombre_cliente')[:50]
		
  	# Añadir clases a campos relevantes
		# for field in ['solicitado', 'comentario', 'compro', 'validacion']:
		# 	if field in self.fields:
		# 		self.fields[field].widget.attrs.update({'class': formclasstext})

	def clean_hora_valida(self):
		hora_valida = self.cleaned_data.get('hora_valida')
		if hora_valida:
			return time(hora_valida.hour, hora_valida.minute)
		return hora_valida

	def clean_hs(self):
		hs = self.cleaned_data.get('hs')
		if hs:
			return time(hs.hour, hs.minute)
		return hs
