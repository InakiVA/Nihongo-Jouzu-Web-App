from django.db import models
from accounts.models import Usuario
from dictionary.models import Palabra
from groups.models import Grupo

# -- Etiquetado global, escalabe y flexible a futuro


class Etiqueta(models.Model):
    etiqueta = models.CharField(max_length=25)
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="etiquetas",
    )

    class Meta:
        db_table = "Etiquetas"

    def __str__(self):
        return self.etiqueta


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

    class Meta:
        unique_together = ("palabra", "etiqueta")
        db_table = "Palabras_Etiquetas"

    def __str__(self):
        return f"{self.palabra.palabra} - {self.etiqueta.etiqueta}"


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

    class Meta:
        unique_together = ("grupo", "etiqueta")
        db_table = "Grupos_Etiquetas"

    def __str__(self):
        return f"{self.grupo.grupo} - {self.etiqueta.etiqueta}"
