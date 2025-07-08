from django.db import models

# -- Autenticación: Registro, login, perfil


class RolUsuario(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"
    MODERATOR = "moderator", "Moderator"


class Usuario(models.Model):
    username = models.CharField(max_length=25, unique=True)
    password_hash = models.TextField()
    role = models.CharField(
        max_length=10,
        choices=RolUsuario.choices,
        default=RolUsuario.USER,
    )

    class Meta:
        db_table = "Usuarios"

    def __str__(self):
        return self.username
