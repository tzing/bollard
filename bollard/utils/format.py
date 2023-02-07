import typing

if typing.TYPE_CHECKING:
    import datetime


def format_iso_time(s: typing.Union[str, "datetime.datetime"]) -> str:
    t = _to_time_object(s)
    t = t.replace(microsecond=0)
    t = t.astimezone()
    return t.isoformat()


def format_relative_time(s: typing.Union[str, "datetime.datetime"]) -> str:
    import humanize
    import datetime

    t = _to_time_object(s)
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    return humanize.naturaltime(now - t)


def format_digest(s: str, short: bool) -> str:
    if short:
        s = s.removeprefix("sha256:")
        return s[:12]  # align docker's default length
    return s


def _to_time_object(s: str) -> "datetime.datetime":
    import datetime

    if isinstance(s, str):
        # docker provides data in ISO format with microseconds and timezone
        # but python's native API does not support so
        s, _ = s.rsplit(".", maxsplit=1)
        t = datetime.datetime.fromisoformat(s)
        t = t.replace(tzinfo=datetime.timezone.utc)
        return t
    elif isinstance(s, datetime.datetime):
        return s
    else:
        raise RuntimeError("Unexpected data type: {}".format(type(s).__name__))


def format_size(s: float) -> str:
    import humanize

    return humanize.naturalsize(s)
