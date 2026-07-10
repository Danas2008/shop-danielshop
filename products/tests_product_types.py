import io

import numpy as np
import soundfile as sf
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from cart.models import CartItem
from orders.models import Order, OrderItem
from products.models import Product
from products.product_types.utils import (
    format_coordinates,
    format_dms,
    generate_waveform_svg,
    parse_spotify_track_url,
)
from products.product_types.gps_plaque import calculate_price as gps_price
from products.product_types.music_plaque import calculate_price as music_price
from products.product_types.soundwave_plaque import calculate_price as soundwave_price
from products.uploads import validate_and_read_audio


def make_wav_bytes(duration_seconds=1.0, samplerate=8000, freq=440.0):
    t = np.linspace(0, duration_seconds, int(samplerate * duration_seconds), endpoint=False)
    data = 0.5 * np.sin(2 * np.pi * freq * t)
    buffer = io.BytesIO()
    sf.write(buffer, data, samplerate, format="WAV")
    buffer.seek(0)
    return buffer.read()


class SpotifyUrlParsingTests(TestCase):
    def test_valid_track_url_returns_id(self):
        track_id = parse_spotify_track_url("https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp")
        self.assertEqual(track_id, "3n3Ppam7vgaVa1iaRUc9Lp")

    def test_valid_track_url_with_query_string(self):
        track_id = parse_spotify_track_url(
            "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp?si=abc123"
        )
        self.assertEqual(track_id, "3n3Ppam7vgaVa1iaRUc9Lp")

    def test_album_url_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_spotify_track_url("https://open.spotify.com/album/3n3Ppam7vgaVa1iaRUc9Lp")

    def test_non_spotify_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_spotify_track_url("https://example.com/track/3n3Ppam7vgaVa1iaRUc9Lp")

    def test_garbage_url_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_spotify_track_url("not a url")


class AudioUploadValidationTests(TestCase):
    def test_valid_wav_is_accepted(self):
        wav_bytes = make_wav_bytes(duration_seconds=1.0)
        upload = SimpleUploadedFile("test.wav", wav_bytes, content_type="audio/wav")
        samples, samplerate = validate_and_read_audio(upload)
        self.assertGreater(len(samples), 0)
        self.assertEqual(samplerate, 8000)

    def test_oversized_file_is_rejected(self):
        wav_bytes = make_wav_bytes(duration_seconds=1.0)
        upload = SimpleUploadedFile("test.wav", wav_bytes, content_type="audio/wav")
        upload.size = 21 * 1024 * 1024  # simulate oversize without allocating real bytes
        with self.assertRaises(ValidationError):
            validate_and_read_audio(upload)

    def test_wrong_format_renamed_as_wav_is_rejected(self):
        upload = SimpleUploadedFile("fake.wav", b"this is not audio data at all", content_type="audio/wav")
        with self.assertRaises(ValidationError):
            validate_and_read_audio(upload)

    def test_mp3_extension_is_rejected_with_czech_message(self):
        upload = SimpleUploadedFile("song.mp3", b"ID3fakecontent", content_type="audio/mpeg")
        with self.assertRaises(ValidationError) as ctx:
            validate_and_read_audio(upload)
        self.assertIn("WAV, OGG nebo FLAC", str(ctx.exception))

    def test_waveform_svg_has_expected_bar_count(self):
        wav_bytes = make_wav_bytes(duration_seconds=2.0)
        upload = SimpleUploadedFile("test.wav", wav_bytes, content_type="audio/wav")
        samples, _ = validate_and_read_audio(upload)
        svg = generate_waveform_svg(samples, bar_count=90)
        self.assertEqual(svg.count("<rect"), 90)


class CoordinateFormattingTests(TestCase):
    def test_known_coordinates_format_correctly(self):
        # Prague castle: 50.0911 N, 14.4016 E
        formatted = format_dms(50.0911, is_lat=True)
        self.assertEqual(formatted, "50°05'28\" S")

        formatted_lng = format_dms(14.4016, is_lat=False)
        self.assertEqual(formatted_lng, "14°24'06\" V")

    def test_negative_coordinates_use_correct_hemisphere(self):
        self.assertTrue(format_dms(-33.8688, is_lat=True).endswith("J"))
        self.assertTrue(format_dms(-70.6693, is_lat=False).endswith("Z"))

    def test_format_coordinates_combines_both(self):
        result = format_coordinates(50.0911, 14.4016)
        self.assertIn(",", result)


class PriceCalculationTests(TestCase):
    def test_music_plaque_price(self):
        self.assertEqual(music_price(None, {}, quantity=1), 549)
        self.assertEqual(music_price(None, {}, quantity=2), 1098)

    def test_soundwave_plaque_price(self):
        self.assertEqual(soundwave_price(None, {}, quantity=1), 599)

    def test_gps_plaque_price(self):
        self.assertEqual(gps_price(None, {}, quantity=1), 499)


@override_settings(ALLOWED_HOSTS=["*"])
class MusicPlaqueEndToEndTests(TestCase):
    def test_add_to_cart_and_checkout_creates_order_item_with_customization(self):
        product = Product.objects.get(slug="hudebni-plaketa")
        client = Client()

        response = client.post(
            reverse("producttype:music_plaque"),
            secure=True,
            data={
                "song_name": "Test Song",
                "artist": "Test Artist",
                "name_line1": "Anna",
                "name_line2": "Petr",
                "date": "1.1.2026",
                "spotify_url": "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.count(), 1)
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.custom_config["product_type"], "music_plaque")
        self.assertEqual(cart_item.custom_config["spotify_track_id"], "3n3Ppam7vgaVa1iaRUc9Lp")

        checkout_data = {
            "customer_name": "Jan Novak",
            "customer_email": "jan@example.com",
            "shipping_address": "Ulice 1",
            "city": "Praha",
            "postal_code": "10000",
            "country": "Czechia",
        }
        response = client.post("/checkout/", checkout_data, secure=True)
        # Stripe call may fail in test env (no network) — order should
        # still be created with structured OrderItem data either way.
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.customization["product_type"], "music_plaque")
        self.assertEqual(order_item.customization["spotify_track_id"], "3n3Ppam7vgaVa1iaRUc9Lp")
        self.assertEqual(order_item.product_type, "music_plaque")
