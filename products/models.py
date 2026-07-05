from django.db import models
from django.urls import reverse


class Product(models.Model):
    CATEGORY_READY_MADE = "ready_made"
    CATEGORY_CUSTOM_STL = "custom_stl"
    CATEGORY_CUSTOM_BUILDER = "custom_builder"
    CATEGORY_CHOICES = [
        (CATEGORY_READY_MADE, "Ready-Made Receipt"),
        (CATEGORY_CUSTOM_STL, "Custom STL Model"),
        (CATEGORY_CUSTOM_BUILDER, "Custom Builder"),
    ]

    TEMPLATE_WEDDING = "wedding"
    TEMPLATE_BREAKUP = "breakup"
    TEMPLATE_DATING = "dating"
    TEMPLATE_DOG = "dog"
    TEMPLATE_FRIENDS = "friends"
    TEMPLATE_CHOICES = [
        (TEMPLATE_WEDDING, "Wedding Anniversary"),
        (TEMPLATE_BREAKUP, "Breakup"),
        (TEMPLATE_DATING, "Start of Dating"),
        (TEMPLATE_DOG, "Getting a Dog"),
        (TEMPLATE_FRIENDS, "Becoming Friends"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    price_base_czk = models.DecimalField(max_digits=8, decimal_places=2)
    price_large_czk = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    magnets_price_czk = models.DecimalField(max_digits=8, decimal_places=2, default=49)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})
