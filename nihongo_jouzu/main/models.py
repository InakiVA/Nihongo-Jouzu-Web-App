from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# __ ENUMERACIONES
class RolUsuario(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"
    MODERATOR = "moderator", "Moderator"


# == MODELOS PRINCIPALES
class Usuario(models.Model):
    username = models.CharField(max_length=25, unique=True)
    password_hash = models.TextField()
    role = models.CharField(
        max_length=10,
        choices=RolUsuario.choices,
        default=RolUsuario.USER,
    )

    class Meta:
        db_table = "Usuarios"

    def __str__(self):
        return self.username


# && AUTOR
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


# && AUTOR
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


# && AUTOR
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


# && PALABRA
# && AUTOR
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


# && PALABRA
# && AUTOR
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


# && PALABRA
# && AUTOR
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


# == TABLAS PUENTE
class UsuarioPalabra(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="usuario_palabras",
    )
    palabra = models.ForeignKey(
        Palabra,
        on_delete=models.CASCADE,
        related_name="palabra_usuarios",
    )
    progreso = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    estrella = models.BooleanField(default=False)

    class Meta:
        unique_together = ("usuario", "palabra")
        db_table = "Usuarios_Palabras"

    def __str__(self):
        return f"{self.usuario.username} ↔ {self.palabra.palabra}"


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

    class Meta:
        unique_together = ("usuario", "grupo")
        db_table = "Usuarios_Grupos"

    def __str__(self):
        return f"{self.usuario.username} ↔ {self.grupo.grupo}"


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
