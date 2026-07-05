from django.db import migrations


READY_MADE = [
    ("Wedding Anniversary Receipt", "wedding-anniversary-receipt", "wedding", "Commemorate your anniversary with a personalized 3D printed receipt."),
    ("Breakup Receipt", "breakup-receipt", "breakup", "A tongue-in-cheek printed receipt to mark the end of a chapter."),
    ("Start of Dating Receipt", "start-of-dating-receipt", "dating", "Celebrate the day you started dating with a keepsake receipt."),
    ("Getting a Dog Receipt", "getting-a-dog-receipt", "dog", "Mark the day you welcomed your new best friend home."),
    ("Becoming Friends Receipt", "becoming-friends-receipt", "friends", "A fun way to commemorate a new friendship."),
]

STL_MODELS = [
    ("Small STL Model", "small-stl-model", 150),
    ("Medium STL Model", "medium-stl-model", 200),
    ("Large STL Model", "large-stl-model", 300),
]


def seed(apps, schema_editor):
    Product = apps.get_model("products", "Product")

    for name, slug, template_type, description in READY_MADE:
        Product.objects.get_or_create(
            slug=slug,
            defaults=dict(
                name=name,
                description=description,
                category="ready_made",
                price_base_czk=350,
                price_large_czk=450,
                magnets_price_czk=49,
                template_type=template_type,
                is_active=True,
            ),
        )

    for name, slug, price in STL_MODELS:
        Product.objects.get_or_create(
            slug=slug,
            defaults=dict(
                name=name,
                description="Print-at-home STL model file.",
                category="custom_stl",
                price_base_czk=price,
                is_active=True,
            ),
        )

    Product.objects.get_or_create(
        slug="custom-receipt-builder",
        defaults=dict(
            name="Custom Receipt Builder",
            description="Design your own receipt from scratch with our live builder.",
            category="custom_builder",
            price_base_czk=400,
            price_large_czk=500,
            magnets_price_czk=49,
            is_active=True,
        ),
    )


def unseed(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    slugs = [s for _, s, *_ in READY_MADE] + [s for _, s, _ in STL_MODELS] + ["custom-receipt-builder"]
    Product.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
