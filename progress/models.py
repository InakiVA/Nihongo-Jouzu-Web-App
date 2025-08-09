from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from dictionary.models import Palabra

# -- Seguimiento del estudio


class UsuarioPalabra(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="usuario_palabras",
    )
    palabra = models.ForeignKey(
        Palabra,
        on_delete=models.CASCADE,
        related_name="palabra_usuarios",
    )
    progreso = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    estrella = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("usuario", "palabra")
        db_table = "Usuarios_Palabras"

    def __str__(self):
        return f"{self.usuario.username} ↔ {self.palabra.palabra}"
