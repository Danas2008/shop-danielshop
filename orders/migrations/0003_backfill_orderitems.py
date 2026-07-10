from decimal import Decimal, InvalidOperation

from django.db import migrations


def backfill_order_items(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    OrderItem = apps.get_model("orders", "OrderItem")

    for order in Order.objects.all().iterator():
        if not order.items:
            continue
        for raw in order.items:
            if not isinstance(raw, dict):
                continue
            try:
                unit_price = Decimal(str(raw.get("unit_price", "0") or "0"))
            except (InvalidOperation, ValueError):
                unit_price = Decimal("0")
            try:
                quantity = int(raw.get("quantity", 1) or 1)
            except (TypeError, ValueError):
                quantity = 1

            OrderItem.objects.create(
                order=order,
                product_id=raw.get("product_id"),
                product_type="receipt_plaque",
                quantity=quantity,
                unit_price_czk=unit_price,
                customization={
                    "product_name": raw.get("product_name", ""),
                    "size": raw.get("size", ""),
                    "custom_config": raw.get("custom_config", {}),
                },
            )


def noop_reverse(apps, schema_editor):
    # Non-destructive backfill; nothing to reverse (Order.items JSON is
    # untouched, so no data is lost by leaving OrderItem rows in place).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_orderitem"),
    ]

    operations = [
        migrations.RunPython(backfill_order_items, noop_reverse),
    ]
