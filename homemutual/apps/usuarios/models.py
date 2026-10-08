# homemutual\apps\usuarios\models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


# class User(AbstractUser):
# 	email = models.EmailField("Correo electrónico")
# 	telefono = models.CharField("Teléfono", max_length=15,
# 							 null=True, blank=True)

class User(AbstractUser):
    email = models.EmailField("Correo electrónico", unique=True)
    telefono = models.CharField(
        "Teléfono",
        max_length=15,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.get_full_name() or 'sin nombre'})"


# -- Al crear un nuevo usuario, que quede activo por defecto.
@receiver(post_save, sender=User)
def set_user_active(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        instance.is_active = True
        instance.save(update_fields=['is_active'])