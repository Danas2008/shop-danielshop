"""Zvuková vlna (soundwave plaque) product type."""
from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

PRICE_CZK = Decimal("599")


class SoundwavePlaqueForm(forms.Form):
    audio_file = forms.FileField(label=_("Audio file (WAV, OGG, FLAC)"), required=False)
    manual_text = forms.CharField(
        label=_("Custom text (if you're not uploading audio)"), max_length=200, required=False
    )
    caption = forms.CharField(label=_("Caption"), max_length=100, required=False)
    date = forms.CharField(label=_("Date"), max_length=20, required=False)

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("audio_file") and not cleaned.get("manual_text"):
            raise forms.ValidationError(
                _("Please upload an audio file, or enter custom text instead of a soundwave.")
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
    "meta_title": _("Soundwave Plaque | DanielsPrints"),
    "meta_description": _(
        "Turn a voice message, song or heartbeat into a visual soundwave printed on a "
        "unique 3D plaque."
    ),
    "preview_template": "products/product_types/soundwave_plaque_preview.html",
}
