from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

import core_views
from products import views as products_views
from products.sitemaps import ProductSitemap

sitemap_view = sitemap
sitemaps = {"products": ProductSitemap}

# Language-independent URLs (never carry a /cs/ or /en/ prefix):
# admin, the language switcher endpoint, JSON/API endpoints, Stripe-facing
# cart/order URLs (hardcoded in JS / called by Stripe), and the sitemap.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/builder/preview/", products_views.builder_preview, name="builder_preview"),
    path("cart/", include("cart.urls")),
    path("", include("orders.urls")),
    path("sitemap.xml", sitemap_view, {"sitemaps": sitemaps}, name="sitemap"),
]

# Crawlable, language-prefixed content URLs (/cs/... and /en/...).
urlpatterns += i18n_patterns(
    path("", core_views.home, name="home"),
    path("about/", core_views.about, name="about"),
    path("contact/", core_views.contact, name="contact"),
    path("terms/", core_views.terms, name="terms"),
    path("privacy/", core_views.privacy, name="privacy"),
    path("shipping/", core_views.shipping, name="shipping"),
    path("shop/", include("products.urls")),
    path("produkt/", include("products.producttype_urls")),
    path("builder/", include("products.builder_urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
