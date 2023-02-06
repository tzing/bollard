import logging
from typing import Iterator, Pattern

logger = logging.getLogger(__name__)

__warned_selector = set()


def is_image_match_selector(metadata: dict, selector: str) -> bool:
    from bollard.utils import split_repo_tag

    for type_, pattern in translate_selector(selector):
        match type_:
            case "ID":
                if pattern.fullmatch(metadata["Id"]):
                    return True
            case "DIGEST":
                values = metadata.get("RepoDigests", [])
                if any(pattern.search(v) for v in values):
                    return True
            case "REGISTRY" | "NAME" | "TAG":
                v_place = {"REGISTRY": 0, "NAME": 1, "TAG": 2}[type_]
                values = set()
                for repo_tag in metadata.get("RepoTags", []):
                    value = split_repo_tag(repo_tag)[v_place]
                    values.add(value)
                if any(pattern.fullmatch(v) for v in values):
                    return True
            case "REPO":
                values = set()
                for repo_tag in metadata.get("RepoTags", []):
                    registry, name, _ = split_repo_tag(repo_tag)
                    if registry:
                        values.add(f"{registry}/{name}")
                    else:
                        values.add(name)
                if any(pattern.fullmatch(v) for v in values):
                    return True
            case "REPO_TAG":
                values = set()
                for repo_tag in metadata.get("RepoTags", []):
                    values.add(repo_tag)
                    registry, name, tag = split_repo_tag(repo_tag)
                    if registry:
                        values.add(f"{name}:{tag}")
                if any(pattern.fullmatch(v) for v in values):
                    return True
    return False


def translate_selector(selector: str) -> list[tuple[str, Pattern]]:
    """Translate selector to regex patterns"""
    output = list(_translate_selector(selector))
    if not output and selector not in __warned_selector:
        logger.warning("Selector '%s' is not a valid pattern", selector)
        __warned_selector.add(selector)
    return output


def _translate_selector(selector: str) -> Iterator[tuple[str, Pattern]]:
    import re

    def build_regex(pattern: str, allowed_chars: str, ignore_case: bool) -> str:
        pattern = pattern.replace(r".", r"\.")
        pattern = pattern.replace(r"*", f"[{allowed_chars}]*")

        flag = re.RegexFlag.ASCII
        if ignore_case:
            flag |= re.RegexFlag.IGNORECASE

        return re.compile(pattern, flag)

    regex_hex = re.compile(r"(sha256:)?([0-9a-f]{2,64})", re.I)
    if m := regex_hex.fullmatch(selector):
        digest = m.group(2).lower()
        yield "ID", re.compile(f"sha256:{digest}[0-9a-f]*")
        yield "DIGEST", re.compile(f"@sha256:{digest}[0-9a-f]*$")

    regex_tag = re.compile(r":([a-z0-9_*][a-z0-9._*-]{,127})", re.I)
    if m := regex_tag.fullmatch(selector):
        pattern = m.group(1)
        pattern = build_regex(pattern, r"a-z0-9._-", True)
        yield "TAG", pattern

    regex_name = re.compile(r"[a-z0-9*][a-z0-9*._-]+", re.I)
    if m := regex_name.fullmatch(selector):
        pattern = selector.lower()
        yield "NAME", build_regex(pattern, r"a-z0-9._-", False)
        yield "REGISTRY", build_regex(pattern, r"a-z0-9.-", False)

        regex_repo = build_regex(pattern, r"a-z0-9/._-", False)
        if selector.startswith("*"):
            yield "REPO", regex_repo
        if selector.endswith("*"):
            yield "REPO", regex_repo

    # test for valid chars
    regex_valid_chars = re.compile(r"([a-z0-9/:*._-]+)")
    if regex_valid_chars.fullmatch(selector):
        regex_any = build_regex(selector, r"a-z0-9/:._-", True)
        if selector.rfind(":") > 0:
            yield "REPO_TAG", regex_any
        elif "/" in selector:
            yield "REPO", regex_any
