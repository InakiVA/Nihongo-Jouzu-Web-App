from django.db import models
from django.conf import settings
from django.db.models import Q

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

    pregunta = None
    respuestas = None

    def set_pregunta_respuesta(self, input_lenguaje, usuario, is_kanji=False):
        if input_lenguaje == "Cualquiera":
            lenguaje_elegido = random.choice(["Original", "Significados"])
        else:
            lenguaje_elegido = input_lenguaje

        if lenguaje_elegido == "Original":
            if not is_kanji:
                if self.palabra != self.lecturas_str(usuario):
                    self.pregunta = [self.palabra, self.lecturas_str(usuario)]
                else:
                    self.pregunta = [self.palabra]
                self.respuestas = ut.set_alternate_inputs(
                    self.significados_list(usuario)
                )
            else:
                self.pregunta = [self.palabra]
                self.respuestas = ut.set_alternate_inputs(
                    self.lecturas_list(usuario) + self.significados_list(usuario)
                )
        elif lenguaje_elegido == "Significados":
            self.pregunta = [self.significados_str(usuario)]
            self.respuestas = ut.set_alternate_inputs(
                [self.palabra] + self.lecturas_list(usuario)
            )

    def update_palabra(self, palabra):
        self.palabra = palabra
        self.save()

    class Meta:
        db_table = "Palabras"

    def __str__(self):
        return self.palabra

    def __lt__(self, other):
        return self.palabra < other.palabra

    def significados_objetos(self, usuario):
        return self.significados.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        )

    def significados_objetos_usuario(self, usuario):
        return self.significados.filter(Q(usuario=usuario))

    def significados_list(self, usuario):
        significados = self.significados_objetos(usuario)
        return sorted([str(s.significado) for s in significados])

    def significados_str(self, usuario):
        significados = self.significados_list(usuario)
        return ", ".join(significados)

    def lecturas_objetos(self, usuario):
        return self.lecturas.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        )

    def lecturas_objetos_usuario(self, usuario):
        return self.lecturas.filter(Q(usuario=usuario))

    def lecturas_list(self, usuario):
        lecturas = self.lecturas_objetos(usuario)
        return sorted([str(l.lectura) for l in lecturas])

    def lecturas_str(self, usuario):
        lecturas = self.lecturas_list(usuario)
        return ", ".join(lecturas)

    def notas_objetos(self, usuario):
        return self.notas.filter(Q(usuario=usuario) | Q(usuario__perfil__rol="admin"))

    def notas_objetos_usuario(self, usuario):
        return self.notas.filter(Q(usuario=usuario))

    def notas_list(self, usuario):
        notas = self.notas_objetos(usuario)
        return sorted([str(n.nota) for n in notas])

    def notas_str(self, usuario):
        notas = self.notas_list(usuario)
        return ", ".join(notas)

    def etiquetas_objetos(self, usuario):
        return self.palabra_etiquetas.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        )

    def etiquetas_objetos_usuario(self, usuario):
        return sorted(self.palabra_etiquetas.filter(Q(usuario=usuario)))

    def etiquetas_list(self, usuario):
        return sorted([str(e.etiqueta) for e in self.etiquetas_objetos(usuario)])

    def grupos_objetos(self, usuario):
        return self.palabra_grupos.filter(
            Q(grupo__usuario=usuario) | Q(grupo__usuario__perfil__rol="admin")
        )

    def grupos_list(self, usuario):
        return sorted([str(g.grupo) for g in self.grupos_objetos(usuario)])

    def grupos_str(self, usuario):
        grupos = self.grupos_list(usuario)
        return ", ".join(grupos)

    def palabras_relacionadas(self, usuario):
        palabras_relacionadas = Palabra.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin"),
            palabra__contains=self.palabra,
        ).exclude(id=self.id)
        palabra_chars = list(self.palabra)
        kanjis_relacionados = Palabra.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin"),
            palabra__in=palabra_chars,
            palabra_etiquetas__etiqueta__etiqueta="Kanji",
        ).exclude(id=self.id)
        return sorted(list(set(palabras_relacionadas | kanjis_relacionados)))


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

    def update_significado(self, significado):
        self.significado = significado
        self.save()

    class Meta:
        db_table = "Significados"

    def __str__(self):
        return f"{self.palabra.palabra}: {self.significado}"


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

    def update_lectura(self, lectura):
        self.lectura = lectura
        self.save()

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

    def update_nota(self, nota):
        self.nota = nota
        self.save()

    class Meta:
        db_table = "Notas"

    def __str__(self):
        return f"{self.palabra.palabra}: {self.nota[:30]}..."
