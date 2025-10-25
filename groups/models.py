from django.db import models
from django.conf import settings
from django.utils import timezone

from dictionary.models import Palabra
from progress.models import UsuarioPalabra


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

    def update_grupo(self, grupo):
        self.grupo = grupo
        self.save()

    def update_descripcion(self, descripcion):
        self.descripcion = descripcion
        self.save()

    @property
    def cantidad_palabras(self):
        return len(self.grupo_palabras.all())

    def grupo_dict(self, usuario="", get_progreso=True):
        return {
            "id": self.id,
            "grupo": self.grupo,
            "descripcion": self.descripcion,
            "cantidad_palabras": self.cantidad_palabras,
            "creador": self.usuario,
            "editable": self.usuario == usuario,
            "fecha_creacion": self.fecha_creacion,
            "ultima_modificacion": self.grupo_usuarios.get(
                usuario=usuario
            ).ultima_modificacion,
            "progreso": (
                self.grupo_usuarios.get(usuario=usuario).progreso if get_progreso else 0
            ),
            "estrella": self.grupo_usuarios.get(usuario=usuario).estrella,
            "estudiando": self.grupo_usuarios.get(usuario=usuario).estudiando,
            "fecha_creacion": self.fecha_creacion,
            "ultima_modificacion": self.grupo_usuarios.get(
                usuario=usuario
            ).ultima_modificacion,
        }

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
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now_add=True)

    def update_modificacion(self):
        self.ultima_modificacion = timezone.now()

    def toggle_estrella(self):
        self.estrella = not self.estrella
        self.save()

    @property
    def progreso(self):
        grupo_palabras = (
            self.grupo.grupo_palabras.all()
        )  # {} instancias de (grupo_id, palabra_id) mediante related_name grupo_palabras
        total = 0
        cantidad = 0

        for gp in grupo_palabras:
            up = UsuarioPalabra.objects.get(
                usuario=self.usuario, palabra=gp.palabra
            )  # {} instancias de progreso (usuario_id, palabra_id, progreso, estrella, ...)
            total += up.progreso
            cantidad += 1
        if cantidad == 0:
            return 0
        return int(total / cantidad)

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
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("grupo", "palabra")
        db_table = "Grupos_Palabras"

    def __str__(self):
        return f"{self.grupo.grupo} - {self.palabra.palabra}"
