"""Souřadnice (GPS coordinates plaque) product type.

Note: this pass uses plain numeric lat/lng entry. A future enhancement
could add an interactive Leaflet map with click-to-pick and Nominatim
reverse geocoding — deliberately out of scope for now.
"""
from decimal import Decimal

from django import forms

from .utils import format_coordinates

PRICE_CZK = Decimal("499")


class GpsPlaqueForm(forms.Form):
    latitude = forms.FloatField(label="Zeměpisná šířka", min_value=-90, max_value=90)
    longitude = forms.FloatField(label="Zeměpisná délka", min_value=-180, max_value=180)
    name_line1 = forms.CharField(label="Jméno / text řádek 1", max_length=60, required=False)
    name_line2 = forms.CharField(label="Jméno / text řádek 2", max_length=60, required=False)
    date = forms.CharField(label="Datum", max_length=20, required=False)
    caption = forms.CharField(label="Popisek (volitelné)", max_length=150, required=False)

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
    "meta_title": "Plaketa se souřadnicemi místa | DanielsPrints",
    "meta_description": (
        "Zvěčněte důležité místo — zadejte GPS souřadnice a vytvořte originální "
        "3D tištěnou plaketu se jmény a datem."
    ),
    "preview_template": "products/product_types/gps_plaque_preview.html",
}
