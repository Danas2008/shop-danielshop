"""Registry of product types.

Each product type module exposes a `CONFIG` dict with:
    slug, name (Czech display name), form_class, price_func(product, form_data, qty),
    meta_title, meta_description, preview_template
"""
from . import gps_plaque, music_plaque, receipt_plaque, soundwave_plaque

PRODUCT_TYPE_REGISTRY = {
    receipt_plaque.CONFIG["slug"]: receipt_plaque.CONFIG,
    music_plaque.CONFIG["slug"]: music_plaque.CONFIG,
    soundwave_plaque.CONFIG["slug"]: soundwave_plaque.CONFIG,
    gps_plaque.CONFIG["slug"]: gps_plaque.CONFIG,
}


def get_product_type(slug):
    return PRODUCT_TYPE_REGISTRY.get(slug)
