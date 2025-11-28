from django.db import models
from django.conf import settings
from dictionary.models import Palabra


# -- Etiquetado global, escalabe y flexible a futuro
class ColorOptions(models.TextChoices):
    COLOR_MAIN = "0", "Main"
    COLOR_A = "A", "Rojo Subrayado"
    COLOR_AA = "AA", "Rojo"
    COLOR_Aa = "Aa", "Rojo Oscuro"
    COLOR_B = "B", "Naranja Subrayado"
    COLOR_BB = "BB", "Naranja"
    COLOR_Bb = "Bb", "Naranja Oscuro"
    COLOR_C = "C", "Amarillo Subrayado"
    COLOR_CC = "CC", "Amarillo"
    COLOR_Cc = "Cc", "Amarillo Oscuro"
    COLOR_D = "D", "Verde Subrayado"
    COLOR_DD = "DD", "Verde"
    COLOR_Dd = "Dd", "Verde Oscuro"
    COLOR_E = "E", "Azul Subrayado"
    COLOR_EE = "EE", "Azul"
    COLOR_Ee = "Ee", "Azul Oscuro"
    COLOR_F = "F", "Indigo Subrayado"
    COLOR_FF = "FF", "Indigo"
    COLOR_Ff = "Ff", "Indigo Oscuro"
    COLOR_G = "G", "Morado Subrayado"
    COLOR_GG = "GG", "Morado"
    COLOR_Gg = "Gg", "Morado Oscuro"
    COLOR_H = "H", "Rosa Subrayado"
    COLOR_HH = "HH", "Rosa"
    COLOR_Hh = "Hh", "Rosa Oscuro"
    COLOR_I = "I", "Dorado Subrayado"
    COLOR_II = "II", "Dorado"
    COLOR_Ii = "Ii", "Dorado Oscuro"
    COLOR_J = "J", "Gris Subrayado"
    COLOR_JJ = "JJ", "Gris"
    COLOR_Jj = "Jj", "Gris Oscuro"
    COLOR_Z = "z", "Neutral"
    COLOR_ZZ = "zz", "Negro"


class Etiqueta(models.Model):
    etiqueta = models.CharField(max_length=25)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="etiquetas",
    )
    color = models.CharField(
        max_length=10,
        choices=ColorOptions.choices,
        default=ColorOptions.COLOR_Z,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

    def update_etiqueta(self, etiqueta):
        self.etiqueta = etiqueta
        self.save()

    def update_color(self, color):
        self.color = color
        self.save()

    class Meta:
        db_table = "Etiquetas"

    def etiqueta_dict(self):
        return {
            "id": self.id,
            "etiqueta": self.etiqueta,
            "color": self.color,
            "creador": self.usuario,
            "fecha_creacion": self.fecha_creacion,
            "ultima_modificacion": self.ultima_modificacion,
        }

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
