from django.urls import path

from . import views_product_types

app_name = "producttype"

urlpatterns = [
    path("hudebni-plaketa/", views_product_types.music_plaque_view, name="music_plaque"),
    path("zvukova-vlna/", views_product_types.soundwave_plaque_view, name="soundwave_plaque"),
    path("souradnice/", views_product_types.gps_plaque_view, name="gps_plaque"),
]
