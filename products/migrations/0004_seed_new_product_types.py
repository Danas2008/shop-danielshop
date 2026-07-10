from django.db import migrations


SEED_PRODUCTS = [
    {
        "name": "Hudební plaketa",
        "slug": "hudebni-plaketa",
        "product_type": "music_plaque",
        "category": "custom_builder",
        "price_base_czk": "549",
        "description": "Originální hudební plaketa s obalem alba, jmény a naskenovatelným Spotify kódem.",
    },
    {
        "name": "Zvuková vlna",
        "slug": "zvukova-vlna",
        "product_type": "soundwave_plaque",
        "category": "custom_builder",
        "price_base_czk": "599",
        "description": "Proměňte hlasovou vzkaz nebo píseň ve vizuální zvukovou vlnu na 3D plaketě.",
    },
    {
        "name": "Souřadnice",
        "slug": "souradnice",
        "product_type": "gps_plaque",
        "category": "custom_builder",
        "price_base_czk": "499",
        "description": "3D tištěná plaketa se zeměpisnými souřadnicemi místa, které je pro vás výjimečné.",
    },
]


def seed_products(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    for data in SEED_PRODUCTS:
        Product.objects.get_or_create(slug=data["slug"], defaults=data)


def remove_products(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    Product.objects.filter(slug__in=[d["slug"] for d in SEED_PRODUCTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_product_product_type"),
    ]

    operations = [
        migrations.RunPython(seed_products, remove_products),
    ]
