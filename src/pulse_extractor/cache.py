import requests_cache


def configure_cache():
    # Cache HTTP requests to avoid re-downloading pages; expire in 1 day.
    requests_cache.install_cache("pulse_cache", backend="sqlite", expire_after=86400)
