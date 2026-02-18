def _to_int(value: str) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def is_version_newer(latest: str, current: str) -> bool:
    """Compare versions like 1.2.3 (best-effort)."""
    latest_parts = [_to_int(p) for p in str(latest).split(".")]
    current_parts = [_to_int(p) for p in str(current).split(".")]

    max_len = max(len(latest_parts), len(current_parts))
    latest_parts += [0] * (max_len - len(latest_parts))
    current_parts += [0] * (max_len - len(current_parts))

    return latest_parts > current_parts
