# neumatic\neumatic\views.py
from django.shortcuts import render, redirect
from django.utils import timezone


def home_view(request):
	if request.user.is_authenticated:
		fecha_actual = timezone.now()
		return render(request, 'home.html', {'fecha': fecha_actual})
	else:
		return redirect('iniciar_sesion')