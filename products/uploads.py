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
from django.utils.translation import gettext as _

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
        raise ValidationError(_("The image is too large. The maximum size is 5 MB."))

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
        raise ValidationError(_("The file is not a valid image. Please upload a JPG, PNG or WEBP."))

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
        raise ValidationError(_("The audio file is too large. The maximum size is 20 MB."))

    name = getattr(uploaded_file, "name", "") or ""
    ext = os.path.splitext(name)[1].lower()
    if ext not in (".wav", ".ogg", ".flac"):
        raise ValidationError(
            _(
                "Unsupported audio format. Please upload a file in WAV, OGG or FLAC format "
                "(MP3 and M4A are not supported)."
            )
        )

    uploaded_file.seek(0)
    raw = uploaded_file.read()
    uploaded_file.seek(0)

    try:
        with sf.SoundFile(io.BytesIO(raw)) as f:
            if f.format not in ALLOWED_AUDIO_FORMATS:
                raise ValidationError(
                    _("Unsupported audio format. Please upload a file in WAV, OGG or FLAC format.")
                )
            duration = len(f) / float(f.samplerate)
            if duration > MAX_AUDIO_SECONDS:
                raise ValidationError(
                    _("The audio recording is too long. The maximum length is %(secs)s seconds.")
                    % {"secs": MAX_AUDIO_SECONDS}
                )
            samples = f.read(dtype="float32", always_2d=True)
            samplerate = f.samplerate
    except ValidationError:
        raise
    except Exception:
        raise ValidationError(
            _("The file could not be read as audio. Please upload a valid WAV, OGG or FLAC file.")
        )

    # Downmix to mono.
    mono = samples.mean(axis=1)
    return mono, samplerate
