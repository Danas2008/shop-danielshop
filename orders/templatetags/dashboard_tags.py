import json
from datetime import timedelta

from django import template
from django.db.models import Count, Sum
from django.utils import timezone

from orders.models import Order

register = template.Library()


@register.simple_tag
def dashboard_stats():
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    paid_orders = Order.objects.exclude(status=Order.STATUS_PENDING)

    revenue_month = paid_orders.filter(created_at__gte=month_start).aggregate(total=Sum("total_price_czk"))["total"] or 0
    revenue_all_time = paid_orders.aggregate(total=Sum("total_price_czk"))["total"] or 0

    orders_month = Order.objects.filter(created_at__gte=month_start).count()
    orders_pending = Order.objects.filter(status=Order.STATUS_PENDING).count()
    orders_shipped = Order.objects.filter(status=Order.STATUS_SHIPPED).count()

    status_counts = dict(Order.objects.values_list("status").annotate(c=Count("id")))
    status_labels = [label for _, label in Order.STATUS_CHOICES]
    status_data = [status_counts.get(key, 0) for key, _ in Order.STATUS_CHOICES]

    top_products = {}
    for order in paid_orders.only("items"):
        for item in order.items:
            name = item.get("product_name", "Unknown")
            top_products[name] = top_products.get(name, 0) + item.get("quantity", 1)
    top_sorted = sorted(top_products.items(), key=lambda kv: kv[1], reverse=True)[:5]

    days = []
    revenue_by_day = []
    for i in range(29, -1, -1):
        day = (now - timedelta(days=i)).date()
        total = paid_orders.filter(created_at__date=day).aggregate(total=Sum("total_price_czk"))["total"] or 0
        days.append(day.strftime("%b %d"))
        revenue_by_day.append(float(total))

    recent_orders = Order.objects.order_by("-created_at")[:10]

    return {
        "revenue_month": revenue_month,
        "revenue_all_time": revenue_all_time,
        "orders_month": orders_month,
        "orders_pending": orders_pending,
        "orders_shipped": orders_shipped,
        "status_labels_json": json.dumps(status_labels),
        "status_data_json": json.dumps(status_data),
        "top_products_labels_json": json.dumps([n for n, _ in top_sorted]),
        "top_products_data_json": json.dumps([c for _, c in top_sorted]),
        "revenue_days_json": json.dumps(days),
        "revenue_data_json": json.dumps(revenue_by_day),
        "recent_orders": recent_orders,
    }
