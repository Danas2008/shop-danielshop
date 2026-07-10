"""Existing 'receipt plaque' (účtenková plaketa) product type.

This wraps the pre-existing builder/customizer behavior with minimal change
so the live product keeps working exactly as before while participating in
the new ProductType registry.
"""
from decimal import Decimal

from django import forms


class ReceiptPlaqueForm(forms.Form):
    store_name = forms.CharField(label="Název obchodu", max_length=60, required=False)
    custom_message = forms.CharField(label="Vlastní zpráva", max_length=200, required=False)
    receipt_date = forms.CharField(label="Datum", max_length=20, required=False)


def calculate_price(product, form_data, quantity=1):
    price = product.price_base_czk if product else Decimal("0")
    return price * quantity


CONFIG = {
    "slug": "receipt_plaque",
    "name": "Účtenková plaketa",
    "form_class": ReceiptPlaqueForm,
    "price_func": calculate_price,
    "meta_title": "Účtenková plaketa na míru | DanielsPrints",
    "meta_description": "Vytvořte si originální 3D tištěnou plaketu ve tvaru účtenky s vlastním textem a datem.",
    "preview_template": "products/product_types/receipt_plaque_preview.html",
}
