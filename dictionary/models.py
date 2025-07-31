from django.db import models
from django.conf import settings

# -- Diccionario central del vocabulario


class Palabra(models.Model):
    palabra = models.CharField(max_length=50)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="palabras",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Palabras"

    def __str__(self):
        return self.palabra

    @property
    def etiquetas_objetos(self):
        return [pe.etiqueta for pe in self.palabra_etiquetas.all()]

    @property
    def etiquetas_list(self):
        return [e.etiqueta for e in self.etiquetas_objetos]

    @property
    def significados_objetos(self):
        return self.significados.all()

    @property
    def significados_str(self):
        return ", ".join([s.significado for s in self.significados_objetos])

    @property
    def lecturas_objetos(self):
        return self.lecturas.all()

    @property
    def lecturas_str(self):
        return ", ".join([l.lectura for l in self.lecturas_objetos])

    @property
    def notas_objetos(self):
        return self.notas.all()

    @property
    def notas_(self):
        return ", ".join([n.nota for n in self.notas_objetos])


class Significado(models.Model):
    significado = models.TextField(max_length=50)
    palabra = models.ForeignKey(
        Palabra,
        on_delete=models.CASCADE,
        related_name="significados",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="significados",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

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
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lecturas",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

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
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notas",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # solo al crear
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Notas"

    def __str__(self):
        return f"{self.palabra.palabra}: {self.nota[:30]}..."
