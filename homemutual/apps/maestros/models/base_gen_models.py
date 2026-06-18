# neumatic\apps\maestros\models\base_gen_models.py
from django.db import models

import socket
from datetime import datetime

# from django.contrib.auth.models import User  

# Importa el modelo User Personalizado
from apps.usuarios.models import User       


class ModeloBaseGenerico(models.Model):
    id_user = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        verbose_name="Usuario Creador",
        null=True, 
        blank=True, 
        default=1,
        related_name='%(class)s_creados'
    )
    id_user_update = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        verbose_name="Usuario Modificador", 
        null=True, 
        blank=True, 
        related_name='%(class)s_modificados'
    )
    usuario = models.CharField(max_length=20, null=True, blank=True)
    estacion = models.CharField(max_length=20, null=True, blank=True)
    fcontrol = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Automático en creación
    fcontrol2 = models.DateTimeField(auto_now=True, null=True, blank=True)     # Automático en actualización
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.estacion:
            self.estacion = socket.gethostname()
        super().save(*args, **kwargs)