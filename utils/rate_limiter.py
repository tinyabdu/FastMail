from core import settings
import time

REQUEST_LOG = {}

def rate_limit(ip: str):
    now = time.time()

    window = settings.RATE_LIMIT_WINDOW
    max_req = settings.RATE_LIMIT_MAX

    if ip not in REQUEST_LOG:
        REQUEST_LOG[ip] = []

    REQUEST_LOG[ip] = [t for t in REQUEST_LOG[ip] if now - t < window]

    if len(REQUEST_LOG[ip]) >= max_req:
        return False

    REQUEST_LOG[ip].append(now)
    return True