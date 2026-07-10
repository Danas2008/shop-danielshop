"""Views for the 3 new customizable product types: music plaque, soundwave
plaque, and GPS coordinates plaque. Each renders a customizer form + a
server-rendered live preview, and on submit adds a configured CartItem
whose custom_config becomes the OrderItem.customization payload at
checkout."""
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from cart.models import CartItem
from cart.views import _get_session_key

from .models import Product
from .product_types import get_product_type
from .product_types.gps_plaque import GpsPlaqueForm
from .product_types.music_plaque import MusicPlaqueForm
from .product_types.soundwave_plaque import SoundwavePlaqueForm
from .product_types.utils import generate_waveform_svg
from .uploads import validate_and_read_audio, validate_and_store_image


def _get_product(product_type_slug):
    return Product.objects.filter(product_type=product_type_slug, is_active=True).first()


def music_plaque_view(request):
    config = get_product_type("music_plaque")
    product = _get_product("music_plaque")
    customization = None
    error = None

    if request.method == "POST":
        form = MusicPlaqueForm(request.POST, request.FILES)
        if form.is_valid():
            album_art_path = None
            album_art_file = form.cleaned_data.get("album_art")
            if album_art_file:
                try:
                    album_art_path = validate_and_store_image(album_art_file)
                except ValidationError as exc:
                    form.add_error("album_art", exc.message if hasattr(exc, "message") else str(exc))

            if not form.errors:
                customization = form.build_customization(album_art_path=album_art_path)
                if album_art_path:
                    from django.core.files.storage import default_storage
                    customization["album_art_url"] = default_storage.url(album_art_path)

                session_key = _get_session_key(request)
                CartItem.objects.create(
                    session_key=session_key,
                    product=product,
                    quantity=1,
                    custom_config={"product_type": "music_plaque", **customization},
                )
                return redirect("cart:detail")
    else:
        form = MusicPlaqueForm()

    return render(
        request,
        "products/product_types/music_plaque_detail.html",
        {
            "product": product,
            "config": config,
            "form": form,
            "customization": customization,
        },
    )


def soundwave_plaque_view(request):
    config = get_product_type("soundwave_plaque")
    product = _get_product("soundwave_plaque")
    customization = None

    if request.method == "POST":
        form = SoundwavePlaqueForm(request.POST, request.FILES)
        if form.is_valid():
            waveform_svg = None
            audio_file = form.cleaned_data.get("audio_file")
            if audio_file:
                try:
                    samples, samplerate = validate_and_read_audio(audio_file)
                    waveform_svg = generate_waveform_svg(samples)
                except ValidationError as exc:
                    form.add_error("audio_file", exc.message if hasattr(exc, "message") else str(exc))
                # Uploaded audio is never persisted to disk in this view —
                # only the extracted waveform SVG is kept.

            if not form.errors:
                customization = {
                    "caption": form.cleaned_data.get("caption", ""),
                    "date": form.cleaned_data.get("date", ""),
                    "manual_text": form.cleaned_data.get("manual_text", ""),
                    "waveform_svg": waveform_svg,
                }
                session_key = _get_session_key(request)
                CartItem.objects.create(
                    session_key=session_key,
                    product=product,
                    quantity=1,
                    custom_config={"product_type": "soundwave_plaque", **customization},
                )
                return redirect("cart:detail")
    else:
        form = SoundwavePlaqueForm()

    return render(
        request,
        "products/product_types/soundwave_plaque_detail.html",
        {
            "product": product,
            "config": config,
            "form": form,
            "customization": customization,
        },
    )


def gps_plaque_view(request):
    config = get_product_type("gps_plaque")
    product = _get_product("gps_plaque")
    customization = None

    if request.method == "POST":
        form = GpsPlaqueForm(request.POST)
        if form.is_valid():
            customization = form.build_customization()
            session_key = _get_session_key(request)
            CartItem.objects.create(
                session_key=session_key,
                product=product,
                quantity=1,
                custom_config={"product_type": "gps_plaque", **customization},
            )
            return redirect("cart:detail")
    else:
        form = GpsPlaqueForm()

    return render(
        request,
        "products/product_types/gps_plaque_detail.html",
        {
            "product": product,
            "config": config,
            "form": form,
            "customization": customization,
        },
    )
