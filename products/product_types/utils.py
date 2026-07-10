"""Shared helpers for product type modules: Spotify URL parsing, coordinate
formatting, and audio waveform SVG generation."""
import re

SPOTIFY_TRACK_RE = re.compile(
    r"^https?://open\.spotify\.com/track/([A-Za-z0-9]{10,30})(?:\?.*)?$"
)


def parse_spotify_track_url(url):
    """Return the Spotify track ID for a valid open.spotify.com track URL.

    Raises ValueError with a Czech-language message if the URL is not a
    valid Spotify *track* URL (rejects albums, playlists, artists, other
    domains, etc). No network calls / API keys involved.
    """
    url = (url or "").strip()
    match = SPOTIFY_TRACK_RE.match(url)
    if not match:
        raise ValueError(
            "Neplatný odkaz na skladbu Spotify. Vložte prosím odkaz ve tvaru "
            "https://open.spotify.com/track/…"
        )
    return match.group(1)


def spotify_code_image_url(track_id):
    return f"https://scannables.scdn.co/uri/plain/png/FFFFFF/black/640/spotify:track:{track_id}"


def format_dms(value, is_lat):
    """Format a decimal degree coordinate as DD°MM'SS\" with hemisphere letter."""
    if is_lat:
        hemisphere = "S" if value >= 0 else "J"
    else:
        hemisphere = "V" if value >= 0 else "Z"
    value = abs(value)
    degrees = int(value)
    minutes_full = (value - degrees) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60)
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1
    return f"{degrees}°{minutes:02d}'{seconds:02d}\" {hemisphere}"


def format_coordinates(lat, lng):
    return f"{format_dms(lat, True)}, {format_dms(lng, False)}"


def generate_waveform_svg(samples, bar_count=100, width=800, height=200):
    """Bucket mono float samples into `bar_count` amplitude bars and render
    a simple SVG bar-chart waveform."""
    if len(samples) == 0:
        samples = [0.0]

    bucket_size = max(1, len(samples) // bar_count)
    bars = []
    for i in range(bar_count):
        start = i * bucket_size
        end = start + bucket_size
        chunk = samples[start:end]
        if len(chunk) == 0:
            bars.append(0.0)
            continue
        amplitude = max(abs(min(chunk)), abs(max(chunk)))
        bars.append(amplitude)

    peak = max(bars) or 1.0
    bars = [b / peak for b in bars]

    bar_width = width / bar_count
    gap = bar_width * 0.25
    mid = height / 2

    rects = []
    for i, amp in enumerate(bars):
        bar_h = max(2, amp * (height * 0.9))
        x = i * bar_width
        y = mid - bar_h / 2
        rects.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{(bar_width - gap):.2f}" '
            f'height="{bar_h:.2f}" rx="1.5" fill="currentColor" />'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" class="waveform-svg">{"".join(rects)}</svg>'
    )
    return svg
