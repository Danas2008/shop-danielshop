import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "customer_name", "total_price_czk", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_id", "customer_name", "customer_email")
    readonly_fields = ("order_id", "stripe_payment_id", "stripe_session_id", "created_at", "paid_at", "shipped_at", "items_pretty")
    fields = (
        "order_id", "status",
        "customer_name", "customer_email", "customer_phone",
        "shipping_address", "city", "postal_code", "country",
        "items_pretty", "total_price_czk",
        "stripe_payment_id", "stripe_session_id",
        "created_at", "paid_at", "shipped_at",
        "notes",
    )
    actions = ["mark_as_shipped", "mark_as_delivered"]

    def items_pretty(self, obj):
        pretty = json.dumps(obj.items, indent=2, ensure_ascii=False)
        return format_html("<pre style='white-space:pre-wrap'>{}</pre>", pretty)

    items_pretty.short_description = "Items"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_SHIPPED, shipped_at=timezone.now())
        self.message_user(request, f"{updated} order(s) marked as shipped.")

    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_DELIVERED)
        self.message_user(request, f"{updated} order(s) marked as delivered.")

    mark_as_delivered.short_description = "Mark selected orders as delivered"
