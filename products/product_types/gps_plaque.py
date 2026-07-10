"""Souřadnice (GPS coordinates plaque) product type.

Note: this pass uses plain numeric lat/lng entry. A future enhancement
could add an interactive Leaflet map with click-to-pick and Nominatim
reverse geocoding — deliberately out of scope for now.
"""
from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

from .utils import format_coordinates

PRICE_CZK = Decimal("499")


class GpsPlaqueForm(forms.Form):
    latitude = forms.FloatField(label=_("Latitude"), min_value=-90, max_value=90)
    longitude = forms.FloatField(label=_("Longitude"), min_value=-180, max_value=180)
    name_line1 = forms.CharField(label=_("Name / text line 1"), max_length=60, required=False)
    name_line2 = forms.CharField(label=_("Name / text line 2"), max_length=60, required=False)
    date = forms.CharField(label=_("Date"), max_length=20, required=False)
    caption = forms.CharField(label=_("Caption (optional)"), max_length=150, required=False)

    def build_customization(self):
        data = self.cleaned_data
        return {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "coordinates_formatted": format_coordinates(data["latitude"], data["longitude"]),
            "name_line1": data.get("name_line1", ""),
            "name_line2": data.get("name_line2", ""),
            "date": data.get("date", ""),
            "caption": data.get("caption", ""),
        }


def calculate_price(product, form_data, quantity=1):
    return PRICE_CZK * quantity


CONFIG = {
    "slug": "gps_plaque",
    "name": "Souřadnice",
    "form_class": GpsPlaqueForm,
    "price_func": calculate_price,
    "price_czk": PRICE_CZK,
    "meta_title": _("Coordinates Plaque of a Place | DanielsPrints"),
    "meta_description": _(
        "Immortalise a meaningful place — enter its GPS coordinates and create a unique "
        "3D-printed plaque with names and a date."
    ),
    "preview_template": "products/product_types/gps_plaque_preview.html",
}
