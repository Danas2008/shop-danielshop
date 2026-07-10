from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product

# Fixed /produkt/<slug>/ URLs for the ProductType-driven customizers
# (products.producttype_urls), keyed by product_type.
PRODUCT_TYPE_URL_NAMES = {
    Product.PRODUCT_TYPE_MUSIC_PLAQUE: "producttype:music_plaque",
    Product.PRODUCT_TYPE_SOUNDWAVE_PLAQUE: "producttype:soundwave_plaque",
    Product.PRODUCT_TYPE_GPS_PLAQUE: "producttype:gps_plaque",
}


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # New ProductType-driven products live at fixed /produkt/ URLs;
        # the legacy receipt plaque keeps its existing /shop/<slug>/ page.
        url_name = PRODUCT_TYPE_URL_NAMES.get(obj.product_type)
        if url_name:
            return reverse(url_name)
        return obj.get_absolute_url()
