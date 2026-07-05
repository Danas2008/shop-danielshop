import json
import logging

import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.models import CartItem

from .models import Order

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


def _cart_items(request):
    session_key = request.session.session_key
    if not session_key:
        return CartItem.objects.none()
    return CartItem.objects.filter(session_key=session_key).select_related("product")


def checkout(request):
    items = list(_cart_items(request))
    subtotal = sum((item.total_price() for item in items), start=0)

    if not items:
        return redirect("cart:detail")

    if request.method == "POST":
        required = ["customer_name", "customer_email", "shipping_address", "city", "postal_code", "country"]
        missing = [f for f in required if not request.POST.get(f)]
        if missing:
            return render(request, "orders/checkout.html", {"items": items, "subtotal": subtotal, "error": "Please fill in all required fields."})

        order_items = [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "size": item.size,
                "custom_config": item.custom_config,
                "unit_price": str(item.unit_price()),
            }
            for item in items
        ]

        order = Order.objects.create(
            customer_name=request.POST["customer_name"],
            customer_email=request.POST["customer_email"],
            customer_phone=request.POST.get("customer_phone", ""),
            shipping_address=request.POST["shipping_address"],
            city=request.POST["city"],
            postal_code=request.POST["postal_code"],
            country=request.POST["country"],
            items=order_items,
            total_price_czk=subtotal,
        )

        success_url = request.build_absolute_uri(reverse("checkout_success", args=[order.order_id]))
        cancel_url = request.build_absolute_uri(reverse("cart:detail"))

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": settings.CURRENCY,
                            "product_data": {"name": item["product_name"]},
                            "unit_amount": int(float(item["unit_price"]) * 100),
                        },
                        "quantity": item["quantity"],
                    }
                    for item in order_items
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=order.customer_email,
                metadata={"order_id": str(order.order_id)},
            )
        except Exception as exc:
            logger.exception("Stripe session creation failed")
            order.notes = f"Stripe error: {exc}"
            order.save(update_fields=["notes"])
            return render(request, "orders/checkout.html", {"items": items, "subtotal": subtotal, "error": "Payment could not be started. Please try again."})

        order.stripe_session_id = session.id
        order.save(update_fields=["stripe_session_id"])

        if request.headers.get("Accept") == "application/json" or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"session_id": session.id, "checkout_url": session.url})
        return redirect(session.url)

    return render(request, "orders/checkout.html", {"items": items, "subtotal": subtotal, "stripe_public_key": settings.STRIPE_PUBLIC_KEY})


def checkout_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if order.status == Order.STATUS_PENDING:
        session_key = request.session.session_key
        if session_key:
            CartItem.objects.filter(session_key=session_key).delete()
    return render(request, "orders/confirmation.html", {"order": order})


def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, "orders/order_detail.html", {"order": order})


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        logger.warning("Invalid Stripe webhook signature")
        return HttpResponse(status=400)

    if event["type"] in ("checkout.session.completed", "payment_intent.succeeded"):
        session = event["data"]["object"]
        order_id = None
        if isinstance(session, dict):
            order_id = session.get("metadata", {}).get("order_id")

        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
                order.status = Order.STATUS_PAID
                order.paid_at = timezone.now()
                order.stripe_payment_id = session.get("payment_intent", "") or session.get("id", "")
                order.save(update_fields=["status", "paid_at", "stripe_payment_id"])
            except Order.DoesNotExist:
                logger.warning("Webhook received for unknown order_id=%s", order_id)

    return HttpResponse(status=200)
