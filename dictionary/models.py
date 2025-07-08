from django.db import models
from accounts.models import Usuario

# -- Diccionario central del vocabulario


class Palabra(models.Model):
    palabra = models.CharField(max_length=50)
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="palabras",
    )

    class Meta:
        db_table = "Palabras"

    def __str__(self):
        return self.palabra


class Significado(models.Model):
    significado = models.TextField(max_length=50)
    palabra = models.ForeignKey(
        Palabra,
        on_delete=models.CASCADE,
        related_name="significados",
    )
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="significados",
    )

    class Meta:
        db_table = "Significados"

    def __str__(self):
        return f"{self.palabra.palabra}: {self.significado}..."


class Lectura(models.Model):
    lectura = models.CharField(max_length=50)
    palabra = models.ForeignKey(
        Palabra,
        on_delete=models.CASCADE,
        related_name="lecturas",
    )
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="lecturas",
    )

    class Meta:
        db_table = "Lecturas"

    def __str__(self):
        return f"{self.palabra.palabra}: {self.lectura}"


class Nota(models.Model):
    nota = models.TextField(max_length=100)
    palabra = models.ForeignKey(
        Palabra,
        on_delete=models.CASCADE,
        related_name="notas",
    )
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="notas",
    )

    class Meta:
        db_table = "Notas"

    def __str__(self):
        return f"{self.palabra.palabra}: {self.nota[:30]}..."
