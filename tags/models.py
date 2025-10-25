from django.db import models
from django.conf import settings
from dictionary.models import Palabra
from groups.models import Grupo

# -- Etiquetado global, escalabe y flexible a futuro


class Etiqueta(models.Model):
    etiqueta = models.CharField(max_length=25)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="etiquetas",
    )
    color = models.CharField(max_length=20, default="neutral")  # neutral, 1, 2, .....
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

    def update_etiqueta(self, etiqueta):
        self.etiqueta = etiqueta
        self.save()

    class Meta:
        db_table = "Etiquetas"

    def __str__(self):
        return self.etiqueta

    def __lt__(self, other):
        return self.etiqueta < other.etiqueta


class PalabraEtiqueta(models.Model):
    palabra = models.ForeignKey(
        Palabra,
        on_delete=models.CASCADE,
        related_name="palabra_etiquetas",
    )
    etiqueta = models.ForeignKey(
        Etiqueta,
        on_delete=models.CASCADE,
        related_name="etiqueta_palabras",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="palabra_etiquetas",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("palabra", "etiqueta", "usuario")
        db_table = "Palabras_Etiquetas"

    def __str__(self):
        return f"{self.palabra.palabra} - {self.etiqueta.etiqueta} ({self.usuario})"

    def __lt__(self, other):
        return self.etiqueta < other.etiqueta


class GrupoEtiqueta(models.Model):
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.CASCADE,
        related_name="grupo_etiquetas",
    )
    etiqueta = models.ForeignKey(
        Etiqueta,
        on_delete=models.CASCADE,
        related_name="etiqueta_grupos",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grupo_etiquetas",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("grupo", "etiqueta", "usuario")
        db_table = "Grupos_Etiquetas"

    def __str__(self):
        return f"{self.grupo.grupo} - {self.etiqueta.etiqueta} ({self.usuario})"
