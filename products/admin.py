from django.contrib import admin
from django.utils.html import format_html

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "category", "price_base_czk", "is_active", "created_at")
    list_display_links = ("thumbnail", "name")
    list_filter = ("category", "is_active", "template_type")
    search_fields = ("name", "slug", "description")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:4px;" />', obj.image.url)
        return "—"

    thumbnail.short_description = "Image"
