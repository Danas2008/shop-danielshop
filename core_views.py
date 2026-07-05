from django.shortcuts import render
from django.contrib import messages

from products.models import Product


def home(request):
    ready_made = Product.objects.filter(category=Product.CATEGORY_READY_MADE, is_active=True)[:5]
    stl_models = Product.objects.filter(category=Product.CATEGORY_CUSTOM_STL, is_active=True)[:6]
    return render(request, "home.html", {"ready_made": ready_made, "stl_models": stl_models})


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
        messages.success(request, "Thanks for reaching out! We'll get back to you within 24 hours.")
    return render(request, "contact.html")
