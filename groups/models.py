from django.db import models
from accounts.models import Usuario
from dictionary.models import Palabra

# -- Atributos de grupos


class Grupo(models.Model):
    grupo = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="grupos",
    )

    class Meta:
        db_table = "Grupos"

    def __str__(self):
        return self.grupo


# Un usuario -> muchos grupos
class UsuarioGrupo(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="usuario_grupos",
    )
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name="grupo_usuarios",
    )
    guardado = models.BooleanField(default=False)
    estudiando = models.BooleanField(default=False)
    estrella = models.BooleanField(default=False)

    class Meta:
        unique_together = ("usuario", "grupo")
        db_table = "Usuarios_Grupos"

    def __str__(self):
        return f"{self.usuario.username} ↔ {self.grupo.grupo}"


# Un grupo -> muchas palabras
class GrupoPalabra(models.Model):
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name="grupo_palabras",
    )
    palabra = models.ForeignKey(
        Palabra,
        on_delete=models.CASCADE,
        related_name="palabra_grupos",
    )

    class Meta:
        unique_together = ("grupo", "palabra")
        db_table = "Grupos_Palabras"

    def __str__(self):
        return f"{self.grupo.grupo} - {self.palabra.palabra}"
