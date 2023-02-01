def split_repo_tag(s: str) -> tuple[str, str, str]:
    r, tag = s.rsplit(":", maxsplit=1)

    si = r.rfind("/")
    if si >= 0:
        registry = r[:si]
        name = r[si + 1 :]
    else:
        registry = ""
        name = r

    return registry, name, tag
