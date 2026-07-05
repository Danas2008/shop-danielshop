from django.contrib import admin

from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("product", "session_key", "quantity", "size", "created_at")
    list_filter = ("size",)
    search_fields = ("session_key",)
