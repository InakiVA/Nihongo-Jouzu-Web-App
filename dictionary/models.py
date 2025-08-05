from django.db import models
from django.conf import settings
import random
import core.utils as ut

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

    def set_pregunta_respuesta(self, input_lenguaje, is_kanji=False):
        if input_lenguaje == "Cualquiera":
            lenguaje_elegido = random.choice(["Original", "Significados"])
        else:
            lenguaje_elegido = input_lenguaje

        if lenguaje_elegido == "Original":
            if not is_kanji:
                if self.palabra != self.lecturas_str:
                    self.pregunta = [self.palabra, self.lecturas_str]
                else:
                    self.pregunta = [self.palabra]
                self.respuestas = ut.set_alternate_inputs(self.significados_list)
            else:
                self.pregunta = [self.palabra]
                self.respuestas = ut.set_alternate_inputs(
                    self.lecturas_list + self.significados_list
                )
        elif lenguaje_elegido == "Significados":
            self.pregunta = self.significados_str
            self.respuestas = ut.set_alternate_inputs(
                [self.palabra] + self.lecturas_list
            )

    class Meta:
        db_table = "Palabras"

    def __str__(self):
        return self.palabra

    @property
    def etiquetas_objetos(self):
        return [pe.etiqueta for pe in self.palabra_etiquetas.all()]

    @property
    def etiquetas_list(self):
        return list(set([str(e.etiqueta) for e in self.etiquetas_objetos]))

    @property
    def significados_objetos(self):
        return self.significados.all()

    @property
    def significados_list(self):
        return list(set([str(s.significado) for s in self.significados_objetos]))

    @property
    def significados_str(self):
        return ", ".join(self.significados_list)

    @property
    def lecturas_objetos(self):
        return self.lecturas.all()

    @property
    def lecturas_list(self):
        return list(set([str(l.lectura) for l in self.lecturas_objetos]))

    @property
    def lecturas_str(self):
        return ", ".join(self.lecturas_list)

    @property
    def notas_objetos(self):
        return self.notas.all()

    @property
    def notas_list(self):
        return list(set([str(n.nota) for n in self.notas_objetos]))

    @property
    def notas_(self):
        return ", ".join(self.notas_list)


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
