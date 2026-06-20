"""Runtime guard for untrusted NLTK resource identifiers."""

from functools import wraps
from urllib.parse import unquote


class UnsafeNltkResourceError(ValueError):
    """Raised when an NLTK resource identifier escapes its data roots."""


def _fully_unquote(value):
    decoded = value
    for _ in range(4):
        next_value = unquote(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    return decoded


def validate_nltk_resource_name(resource_name):
    """Reject absolute and parent-traversing NLTK resource paths."""
    if not isinstance(resource_name, str):
        return

    decoded = _fully_unquote(resource_name)
    if decoded.lower().startswith("nltk:"):
        decoded = decoded[5:]

    normalized = decoded.replace("\\", "/")
    path_parts = normalized.split("/")
    drive_absolute = (
        len(normalized) >= 3
        and normalized[1] == ":"
        and normalized[2] == "/"
    )
    if (
        normalized.startswith("/")
        or drive_absolute
        or any(part == ".." for part in path_parts)
    ):
        raise UnsafeNltkResourceError("Unsafe NLTK resource path rejected")


def install_nltk_load_guard(nltk_module):
    """Wrap nltk.data.load once so decoded paths are checked before loading."""
    original_load = getattr(nltk_module.data, "load", None)
    if original_load is None:
        return
    if getattr(original_load, "_valleybot_path_guard", False):
        return

    @wraps(original_load)
    def guarded_load(resource_url, *args, **kwargs):
        validate_nltk_resource_name(resource_url)
        return original_load(resource_url, *args, **kwargs)

    guarded_load._valleybot_path_guard = True
    nltk_module.data.load = guarded_load
