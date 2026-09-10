from slugify import slugify


class SlugifyAdminMixin:
    """Auto-generate English slug from a source field on save."""
    slugify_from = "name"

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            setattr(obj, "slug", slugify(getattr(obj, self.slugify_from)))
        super().save_model(request, obj, form, change)
