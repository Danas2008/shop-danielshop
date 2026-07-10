from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _


def home(request):
    # Showcase all four personalized-gift product types with equal weight.
    showcase = [
        {
            "name": _("Receipt Plaque"),
            "pitch": _("Your milestone moment as a 3D-printed keepsake receipt."),
            "price": 400,
            "url": reverse("builder:index"),
            "image": "images/products/receipt_plaque.svg",
        },
        {
            "name": _("Music Plaque"),
            "pitch": _("A favourite song, framed with a scannable Spotify code."),
            "price": 549,
            "url": reverse("producttype:music_plaque"),
            "image": "images/products/music_plaque.svg",
        },
        {
            "name": _("Soundwave Plaque"),
            "pitch": _("Turn a voice message or song into a printed soundwave."),
            "price": 599,
            "url": reverse("producttype:soundwave_plaque"),
            "image": "images/products/soundwave_plaque.svg",
        },
        {
            "name": _("Coordinates Plaque"),
            "pitch": _("Immortalise a special place by its GPS coordinates."),
            "price": 499,
            "url": reverse("producttype:gps_plaque"),
            "image": "images/products/gps_plaque.svg",
        },
    ]
    return render(request, "home.html", {"showcase": showcase})


def about(request):
    return render(request, "about.html")


def terms(request):
    return render(request, "terms.html")


def privacy(request):
    return render(request, "privacy.html")


def shipping(request):
    return render(request, "shipping.html")


def contact(request):
    if request.method == "POST":
        messages.success(request, _("Thanks for reaching out! We'll get back to you within 24 hours."))
    return render(request, "contact.html")
