"""Zvuková vlna (soundwave plaque) product type."""
from decimal import Decimal

from django import forms

PRICE_CZK = Decimal("599")


class SoundwavePlaqueForm(forms.Form):
    audio_file = forms.FileField(label="Zvukový soubor (WAV, OGG, FLAC)", required=False)
    manual_text = forms.CharField(
        label="Vlastní text (pokud nenahráváte zvuk)", max_length=200, required=False
    )
    caption = forms.CharField(label="Popisek", max_length=100, required=False)
    date = forms.CharField(label="Datum", max_length=20, required=False)

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("audio_file") and not cleaned.get("manual_text"):
            raise forms.ValidationError(
                "Nahrajte prosím zvukový soubor, nebo zadejte vlastní text místo zvukové vlny."
            )
        return cleaned


def calculate_price(product, form_data, quantity=1):
    return PRICE_CZK * quantity


CONFIG = {
    "slug": "soundwave_plaque",
    "name": "Zvuková vlna",
    "form_class": SoundwavePlaqueForm,
    "price_func": calculate_price,
    "price_czk": PRICE_CZK,
    "meta_title": "Plaketa se zvukovou vlnou | DanielsPrints",
    "meta_description": (
        "Proměňte hlasovou vzkaz, píseň nebo tlukot srdce ve vizuální zvukovou vlnu "
        "vytištěnou na originální 3D plaketě."
    ),
    "preview_template": "products/product_types/soundwave_plaque_preview.html",
}
