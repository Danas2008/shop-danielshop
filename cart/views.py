import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .models import CartItem


def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


@require_POST
def cart_add(request):
    session_key = _get_session_key(request)

    if request.content_type == "application/json":
        data = json.loads(request.body or "{}")
    else:
        data = request.POST

    product = get_object_or_404(Product, pk=data.get("product_id"), is_active=True)
    quantity = int(data.get("quantity", 1) or 1)
    size = data.get("size", CartItem.SIZE_STANDARD)

    custom_config = data.get("custom_config") or {}
    if isinstance(custom_config, str):
        try:
            custom_config = json.loads(custom_config)
        except json.JSONDecodeError:
            custom_config = {}
    if data.get("add_magnets") in ("true", "on", True, "1"):
        custom_config["add_magnets"] = True

    CartItem.objects.create(
        session_key=session_key,
        product=product,
        quantity=quantity,
        size=size,
        custom_config=custom_config,
    )

    count = CartItem.objects.filter(session_key=session_key).count()
    return JsonResponse({"success": True, "cart_count": count})


def cart_detail(request):
    session_key = _get_session_key(request)
    items = CartItem.objects.filter(session_key=session_key).select_related("product")
    subtotal = sum((item.total_price() for item in items), start=0)
    return render(request, "cart/cart.html", {"items": items, "subtotal": subtotal})


@require_POST
def cart_remove(request, item_id):
    session_key = _get_session_key(request)
    CartItem.objects.filter(pk=item_id, session_key=session_key).delete()
    return redirect("cart:detail")


@require_POST
def cart_update(request, item_id):
    session_key = _get_session_key(request)
    item = get_object_or_404(CartItem, pk=item_id, session_key=session_key)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1
    item.quantity = max(1, quantity)
    item.save()
    return redirect("cart:detail")
