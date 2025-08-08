from django.db import migrations, models
from django.conf import settings
from django.utils import timezone
import django.db.models.deletion


def set_defaults(apps, schema_editor):
    # Use lowercase app labels here
    PalabraEtiqueta = apps.get_model("tags", "PalabraEtiqueta")
    GrupoEtiqueta = apps.get_model("tags", "GrupoEtiqueta")

    # Get the swappable user model via apps
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)

    # Pick your backfill user
    my_user = User.objects.get(username="japanese_manager")

    now = timezone.now()
    # Only rows where usuario is NULL (new field just added)
    PalabraEtiqueta.objects.filter(usuario__isnull=True).update(
        usuario=my_user, created_at=now
    )
    GrupoEtiqueta.objects.filter(usuario__isnull=True).update(
        usuario=my_user, created_at=now
    )


class Migration(migrations.Migration):

    dependencies = [
        ("dictionary", "0005_rename_autor_lectura_usuario_and_more"),
        ("groups", "0007_rename_autor_grupo_usuario"),
        ("tags", "0003_rename_autor_etiqueta_usuario"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1) Remove old unique_together only in STATE (skip DB drop to avoid the error)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterUniqueTogether(
                    name="grupoetiqueta", unique_together=set()
                ),
                migrations.AlterUniqueTogether(
                    name="palabraetiqueta", unique_together=set()
                ),
            ],
            database_operations=[],
        ),
        # 2) Add new fields; allow NULL for backfill
        migrations.AddField(
            model_name="grupoetiqueta",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="grupoetiqueta",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="grupo_etiquetas",
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="palabraetiqueta",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="palabraetiqueta",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="palabra_etiquetas",
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        # 3) Backfill usuario + created_at
        migrations.RunPython(set_defaults),
        # 4) Make created_at non-nullable (optional; safe since backfilled)
        migrations.AlterField(
            model_name="grupoetiqueta",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="palabraetiqueta",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        # 5) Make usuario non-nullable after backfill
        migrations.AlterField(
            model_name="grupoetiqueta",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="grupo_etiquetas",
                to=settings.AUTH_USER_MODEL,
                null=False,
            ),
        ),
        migrations.AlterField(
            model_name="palabraetiqueta",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="palabra_etiquetas",
                to=settings.AUTH_USER_MODEL,
                null=False,
            ),
        ),
        # 6) Add new user-scoped unique constraints
        migrations.AddConstraint(
            model_name="grupoetiqueta",
            constraint=models.UniqueConstraint(
                fields=["grupo", "etiqueta", "usuario"],
                name="uniq_grupo_etiqueta_usuario",
            ),
        ),
        migrations.AddConstraint(
            model_name="palabraetiqueta",
            constraint=models.UniqueConstraint(
                fields=["palabra", "etiqueta", "usuario"],
                name="uniq_palabra_etiqueta_usuario",
            ),
        ),
    ]
