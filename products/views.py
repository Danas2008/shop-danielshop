import json
from decimal import Decimal

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Product

BUILDER_TEMPLATE_MESSAGES = {
    Product.TEMPLATE_WEDDING: "Happy Anniversary",
    Product.TEMPLATE_BREAKUP: "Thanks for the memories",
    Product.TEMPLATE_DATING: "Our first date",
    Product.TEMPLATE_DOG: "Welcome home, pup",
    Product.TEMPLATE_FRIENDS: "Friends since",
}


def product_list(request):
    category = request.GET.get("category")
    products = Product.objects.filter(is_active=True)
    if category in dict(Product.CATEGORY_CHOICES):
        products = products.filter(category=category)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "products/listing.html",
        {"page_obj": page_obj, "category": category, "categories": Product.CATEGORY_CHOICES},
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)[:4]
    )
    return render(request, "products/detail.html", {"product": product, "related": related})


def builder(request):
    templates = Product.TEMPLATE_CHOICES
    builder_product = Product.objects.filter(category=Product.CATEGORY_CUSTOM_BUILDER, is_active=True).first()
    return render(request, "products/builder.html", {"templates": templates, "builder_product": builder_product})


@require_POST
def builder_preview(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        data = request.POST

    store_name = str(data.get("store_name", ""))[:60]
    items = data.get("items") or []
    message = str(data.get("custom_message", ""))[:200]
    receipt_date = str(data.get("receipt_date", ""))[:20]
    height = data.get("height", "12")

    line_items = []
    total = Decimal("0")
    for item in items[:3]:
        name = str(item.get("name", ""))[:40]
        try:
            price = Decimal(str(item.get("price", 0) or 0))
        except Exception:
            price = Decimal("0")
        if name:
            line_items.append({"name": name, "price": price})
            total += price

    return JsonResponse(
        {
            "store_name": store_name,
            "items": [{"name": i["name"], "price": str(i["price"])} for i in line_items],
            "total": str(total),
            "message": message,
            "date": receipt_date,
            "height": height,
        }
    )
