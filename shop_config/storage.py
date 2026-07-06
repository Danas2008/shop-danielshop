from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class NonStrictManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Falls back to the unhashed filename instead of raising when a
    static reference (e.g. Jazzmin's dynamic Bootswatch theme paths)
    has no manifest entry."""

    manifest_strict = False
