"""Existing 'receipt plaque' (účtenková plaketa) product type.

This wraps the pre-existing builder/customizer behavior with minimal change
so the live product keeps working exactly as before while participating in
the new ProductType registry.
"""
from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _


class ReceiptPlaqueForm(forms.Form):
    store_name = forms.CharField(label=_("Store name"), max_length=60, required=False)
    custom_message = forms.CharField(label=_("Custom message"), max_length=200, required=False)
    receipt_date = forms.CharField(label=_("Date"), max_length=20, required=False)


def calculate_price(product, form_data, quantity=1):
    price = product.price_base_czk if product else Decimal("0")
    return price * quantity


CONFIG = {
    "slug": "receipt_plaque",
    "name": "Účtenková plaketa",
    "form_class": ReceiptPlaqueForm,
    "price_func": calculate_price,
    "meta_title": _("Custom Receipt Plaque | DanielsPrints"),
    "meta_description": _(
        "Design your own 3D-printed receipt-shaped plaque with custom text and date — a "
        "unique keepsake gift made to order."
    ),
    "preview_template": "products/product_types/receipt_plaque_preview.html",
}
