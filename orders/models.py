import uuid

from django.db import models

from products.models import Product


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50, blank=True)
    shipping_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    items = models.JSONField(default=list)
    total_price_czk = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)

    stripe_payment_id = models.CharField(max_length=255, blank=True)
    stripe_session_id = models.CharField(max_length=255, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_id} ({self.customer_name})"


class OrderItem(models.Model):
    """Structured per-line-item record for an order. Introduced alongside
    the ProductType registry; Order.items JSONField is kept in place
    unused for backward compatibility (non-destructive migration)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    product_type = models.CharField(max_length=30, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_czk = models.DecimalField(max_digits=8, decimal_places=2)
    customization = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        name = self.product.name if self.product else "(smazaný produkt)"
        return f"{name} x{self.quantity}"

    def total_price(self):
        return self.unit_price_czk * self.quantity
