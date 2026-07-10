from django.test import SimpleTestCase

from .models import Product


class ProductImageFallbackTests(SimpleTestCase):
    def test_placeholder_image_is_used_when_product_has_no_upload(self):
        product = Product(name="Sample", slug="sample", category=Product.CATEGORY_READY_MADE, price_base_czk=100)

        image_url = product.get_display_image_url()

        self.assertIn("product-placeholder.svg", image_url)

    def test_uploaded_image_takes_precedence_over_placeholder(self):
        product = Product(
            name="Sample",
            slug="sample-2",
            category=Product.CATEGORY_READY_MADE,
            price_base_czk=100,
            image="products/demo.jpg",
        )

        image_url = product.get_display_image_url()

        self.assertIn("products/demo.jpg", image_url)
