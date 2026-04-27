
from urllib.parse import urlparse


def identify_domain(url):
    if not isinstance(url, str) or not url.strip():
        return "unknown"

    candidate = url.strip()
    if "//" not in candidate:
        candidate = f"https://{candidate}"

    try:
        parsed = urlparse(candidate)
    except ValueError:
        return "unknown"

    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]

    if "twitter.com" in host or host == "x.com" or host.endswith(".x.com"):
        return "x"
    if "instagram.com" in host:
        return "instagram"
    if "facebook.com" in host or "fb.watch" in host:
        return "facebook"
    if "tiktok.com" in host:
        return "tiktok"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    return "unknown"
    
