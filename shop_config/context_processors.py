from django.conf import settings
from django.urls import translate_url


def i18n_alternates(request):
    """Expose per-language alternate URLs for the current page so templates
    can emit hreflang tags and a language switcher. For non-prefixed URLs
    translate_url returns the same path, which is harmless."""
    current = request.get_full_path()
    alternates = []
    for code, name in settings.LANGUAGES:
        alternates.append(
            {
                "code": code,
                "name": name,
                "url": translate_url(current, code),
                "absolute_url": request.build_absolute_uri(translate_url(current, code)),
            }
        )
    return {"i18n_alternates": alternates}
