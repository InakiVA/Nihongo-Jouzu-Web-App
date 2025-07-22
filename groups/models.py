from django.db import models
from django.conf import settings
from dictionary.models import Palabra
from progress.models import UsuarioPalabra

# -- Atributos de grupos


class Grupo(models.Model):
    grupo = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grupos",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Grupos"

    def __str__(self):
        return self.grupo


# Un usuario -> muchos grupos
class UsuarioGrupo(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="usuario_grupos",
    )
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name="grupo_usuarios",
    )
    estudiando = models.BooleanField(default=False)
    estrella = models.BooleanField(default=False)

    @property
    def progreso(self):
        grupo_palabras = (
            self.grupo.grupo_palabras.all()
        )  # {} instancias de (grupo_id, palabra_id) mediante related_name grupo_palabras
        total = 0
        cantidad = 0

        for gp in grupo_palabras:
            try:
                up = UsuarioPalabra.objects.get(
                    usuario=self.usuario, palabra=gp.palabra
                )  # {} instancias de progreso (usuario_id, palabra_id, progreso, estrella, ...)
                total += up.progreso
                cantidad += 1
            except UsuarioPalabra.DoesNotExist:
                continue  # Si no ha estudiado esa palabra, la ignoramos

        if cantidad == 0:
            return 0
        return total / cantidad

    class Meta:
        unique_together = ("usuario", "grupo")
        db_table = "settings.AUTH_USER_MODELs_Grupos"

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
