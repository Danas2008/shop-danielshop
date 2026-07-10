"""Shared upload validation/storage helpers.

Images are verified with Pillow (opened + verified, EXIF stripped on save).
Audio is verified with `soundfile` (pure-Python bindings to libsndfile via
wheels — no ffmpeg / system binary required). Only WAV, OGG and FLAC are
accepted since those are the formats soundfile can decode without ffmpeg.
"""
import io
import os
import uuid

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_AUDIO_BYTES = 20 * 1024 * 1024  # 20MB
MAX_AUDIO_SECONDS = 60

ALLOWED_AUDIO_FORMATS = {"WAV", "OGG", "FLAC"}


def _upload_dir():
    return f"uploads/{uuid.uuid4()}"


def validate_and_store_image(uploaded_file):
    """Validate an uploaded image with Pillow, strip EXIF, and store it
    under media/uploads/<uuid>/. Returns the storage path.

    Raises django.core.exceptions.ValidationError (Czech message) on any
    problem.
    """
    from PIL import Image, UnidentifiedImageError

    if uploaded_file.size > MAX_IMAGE_BYTES:
        raise ValidationError("Obrázek je příliš velký. Maximální velikost je 5 MB.")

    uploaded_file.seek(0)
    raw = uploaded_file.read()
    uploaded_file.seek(0)

    try:
        image = Image.open(io.BytesIO(raw))
        image.verify()
        # verify() poisons the image object; re-open for actual processing.
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError("Soubor není platný obrázek. Nahrajte prosím JPG, PNG nebo WEBP.")

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGBA")
    else:
        image = image.convert("RGB")

    # Re-save without EXIF metadata.
    buffer = io.BytesIO()
    save_format = "PNG" if image.mode == "RGBA" else "JPEG"
    image.save(buffer, format=save_format)
    buffer.seek(0)

    ext = "png" if save_format == "PNG" else "jpg"
    path = f"{_upload_dir()}/image.{ext}"
    stored_path = default_storage.save(path, ContentFile(buffer.read()))
    return stored_path


def validate_and_read_audio(uploaded_file):
    """Validate an uploaded audio file with soundfile. Returns
    (samples, samplerate) as a mono float array. Does NOT persist the file
    to disk long-term — caller is responsible for deleting any temp copy
    immediately after use.

    Raises django.core.exceptions.ValidationError (Czech message) on any
    problem.
    """
    import soundfile as sf

    if uploaded_file.size > MAX_AUDIO_BYTES:
        raise ValidationError("Zvukový soubor je příliš velký. Maximální velikost je 20 MB.")

    name = getattr(uploaded_file, "name", "") or ""
    ext = os.path.splitext(name)[1].lower()
    if ext not in (".wav", ".ogg", ".flac"):
        raise ValidationError(
            "Nepodporovaný formát zvuku. Nahrajte prosím soubor ve formátu WAV, OGG nebo FLAC "
            "(MP3 a M4A nejsou podporovány)."
        )

    uploaded_file.seek(0)
    raw = uploaded_file.read()
    uploaded_file.seek(0)

    try:
        with sf.SoundFile(io.BytesIO(raw)) as f:
            if f.format not in ALLOWED_AUDIO_FORMATS:
                raise ValidationError(
                    "Nepodporovaný formát zvuku. Nahrajte prosím soubor ve formátu WAV, OGG nebo FLAC."
                )
            duration = len(f) / float(f.samplerate)
            if duration > MAX_AUDIO_SECONDS:
                raise ValidationError(
                    f"Zvuková nahrávka je příliš dlouhá. Maximální délka je {MAX_AUDIO_SECONDS} sekund."
                )
            samples = f.read(dtype="float32", always_2d=True)
            samplerate = f.samplerate
    except ValidationError:
        raise
    except Exception:
        raise ValidationError(
            "Soubor se nepodařilo přečíst jako zvuk. Nahrajte prosím platný WAV, OGG nebo FLAC soubor."
        )

    # Downmix to mono.
    mono = samples.mean(axis=1)
    return mono, samplerate
