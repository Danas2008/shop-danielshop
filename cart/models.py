from django.db import models

from products.models import Product


class CartItem(models.Model):
    SIZE_STANDARD = "standard"
    SIZE_LARGE = "large"
    SIZE_CHOICES = [
        (SIZE_STANDARD, "Standard"),
        (SIZE_LARGE, "Large"),
    ]

    session_key = models.CharField(max_length=64, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default=SIZE_STANDARD)
    custom_config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.product.name} x{self.quantity} ({self.session_key[:8]})"

    def unit_price(self):
        price = self.product.price_base_czk
        if self.size == self.SIZE_LARGE and self.product.price_large_czk:
            price = self.product.price_large_czk
        if self.custom_config.get("add_magnets"):
            price += self.product.magnets_price_czk
        return price

    def total_price(self):
        return self.unit_price() * self.quantity
