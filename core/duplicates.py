# python manage.py shell
from django.db import transaction
from django.db.models import Min, Count
from tags.models import PalabraEtiqueta, GrupoEtiqueta
from dictionary.models import Palabra, Significado, Lectura, Nota


def dedupe_model(Model, fields):
    """
    Keep the lowest id in each duplicate group partitioned by `fields`,
    delete all other rows in that group.
    """
    with transaction.atomic():
        dup_groups = (
            Model.objects.values(*fields)
            .annotate(min_id=Min("id"), cnt=Count("id"))
            .filter(cnt__gt=1)
        )

        to_delete_ids = []
        for g in dup_groups:
            # Build a filter matching the group
            filt = {k: g[k] for k in fields}
            # Collect all ids in the group except the min_id
            to_delete_ids.extend(
                list(
                    Model.objects.filter(**filt)
                    .exclude(id=g["min_id"])
                    .values_list("id", flat=True)
                )
            )

        if to_delete_ids:
            Model.objects.filter(id__in=to_delete_ids).delete()
        return len(to_delete_ids)


# --- Choose your fields ---
# If you want “logical” duplicates (recommended):
pe_fields = ["palabra_id", "etiqueta_id", "usuario_id"]  # ignore created_at
ge_fields = ["grupo_id", "etiqueta_id", "usuario_id"]
pl_fields = ["palabra_id", "etiqueta_id", "usuario_id"]


# If you really want the *entire row* (strict):
# pe_fields = ['palabra_id', 'etiqueta_id', 'usuario_id', 'created_at']
# ge_fields = ['grupo_id', 'etiqueta_id', 'usuario_id', 'created_at']

deleted_pe = dedupe_model(PalabraEtiqueta, pe_fields)
deleted_ge = dedupe_model(GrupoEtiqueta, ge_fields)
print(
    f"Deleted {deleted_pe} PalabraEtiqueta duplicates, {deleted_ge} GrupoEtiqueta duplicates"
)
