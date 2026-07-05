from django.urls import path

from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<uuid:order_id>/", views.checkout_success, name="checkout_success"),
    path("stripe-webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("orders/<uuid:order_id>/", views.order_detail, name="order_detail"),
]
