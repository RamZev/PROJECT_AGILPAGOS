# apps/core/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo staff (backoffice)."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "No tenés permisos para acceder a esta sección (staff).")
        return redirect("home")

class SocioRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo socio (usuario final), explícitamente excluye staff."""
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Sección exclusiva para socios.")
        return redirect("home")
