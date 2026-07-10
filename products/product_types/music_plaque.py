"""Hudební plaketa (music plaque) product type."""
from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

from .utils import parse_spotify_track_url, spotify_code_image_url

PRICE_CZK = Decimal("549")


class MusicPlaqueForm(forms.Form):
    song_name = forms.CharField(label=_("Song name"), max_length=100)
    artist = forms.CharField(label=_("Artist"), max_length=100)
    album_art = forms.ImageField(label=_("Album art (optional)"), required=False)
    name_line1 = forms.CharField(label=_("Name / text line 1"), max_length=60, required=False)
    name_line2 = forms.CharField(label=_("Name / text line 2"), max_length=60, required=False)
    date = forms.CharField(label=_("Date"), max_length=20, required=False)
    spotify_url = forms.CharField(label=_("Spotify track link"), max_length=300)

    def clean_spotify_url(self):
        url = self.cleaned_data["spotify_url"]
        try:
            track_id = parse_spotify_track_url(url)
        except ValueError as exc:
            raise forms.ValidationError(str(exc))
        self.cleaned_data["spotify_track_id"] = track_id
        return url

    def build_customization(self, album_art_path=None):
        data = self.cleaned_data
        track_id = data.get("spotify_track_id") or parse_spotify_track_url(data["spotify_url"])
        return {
            "song_name": data["song_name"],
            "artist": data["artist"],
            "name_line1": data.get("name_line1", ""),
            "name_line2": data.get("name_line2", ""),
            "date": data.get("date", ""),
            "spotify_url": data["spotify_url"],
            "spotify_track_id": track_id,
            "spotify_code_url": spotify_code_image_url(track_id),
            "album_art_path": album_art_path,
        }


def calculate_price(product, form_data, quantity=1):
    return PRICE_CZK * quantity


CONFIG = {
    "slug": "music_plaque",
    "name": "Hudební plaketa",
    "form_class": MusicPlaqueForm,
    "price_func": calculate_price,
    "price_czk": PRICE_CZK,
    "meta_title": _("Music Plaque with Spotify Code | DanielsPrints"),
    "meta_description": _(
        "A personalized music plaque with album art, names and a scannable Spotify code. "
        "Give a favourite song as a 3D-printed keepsake."
    ),
    "preview_template": "products/product_types/music_plaque_preview.html",
}
