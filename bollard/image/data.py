import collections.abc
import logging
import re
from typing import Any, Iterator, Sequence

import click

from bollard.utils import check_docker_output

FULL_LENGTH = 64

logger = logging.getLogger(__name__)
regex_sha = re.compile(r"(?:sha256:)?([0-9a-f]{2,64})", re.RegexFlag.IGNORECASE)

__cache_image_data = None


def list_image_ids(incl_interm_img: bool = False, filters: list[str] = ()) -> list[str]:
    args = ["images", "--quiet", "--no-trunc"]
    if incl_interm_img:
        args += ["--all"]
    for f in filters:
        args += ["--filter", f]
    data_bytes = check_docker_output(args, use_context=False)
    data_str = data_bytes.rstrip().decode()

    # output id from docker could be duplicated
    # builtin dict is ordered, use it to preserve the order
    unique_id_collection = {}
    for id_ in data_str.splitlines():
        unique_id_collection[id_] = None
    return list(unique_id_collection)


def inspect_image(image_ids: list[str]) -> list[dict[str, Any]]:
    """Wrap `docker inspect` command and cache the result."""
    global __cache_image_data
    import json

    if __cache_image_data is None:
        __cache_image_data = PrefixDict()

    output = []

    # use cache
    query_ids = []
    for id_ in image_ids:
        if data := __cache_image_data.get(id_):
            output.append(data)
        else:
            query_ids.append(id_)

    # query
    if query_ids:
        data_bytes = check_docker_output(
            ["inspect", "--type", "image", *query_ids], use_context=False
        )
        for data in json.loads(data_bytes):
            id_ = data["Id"]
            __cache_image_data[id_] = data
            output.append(data)

    # check all requested data are fetched
    # the request id could be prefix only so we should comparing through the count
    request_ids = set(image_ids)
    output_ids = {d["Id"] for d in output}
    if len(request_ids) != len(output_ids):
        missing_ids = request_ids - output_ids
        for id_ in missing_ids:
            logger.warning("No such image: %s", id_)

    return output


class PrefixDict(collections.abc.MutableMapping[str, Any]):
    """A dict object that matches the prefix on key."""

    def __init__(self):
        self._data: dict[str, Any] = {}
        self._alias: dict[str, str] = {}

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, __key: str) -> Any:
        m = regex_sha.fullmatch(__key)
        if not m:
            raise KeyError(__key)

        # direct query
        sha = m.group(1).lower()
        if len(sha) == FULL_LENGTH:
            return self._data[sha]

        if orig_key := self._alias.get(sha):
            return self._data[orig_key]

        # match
        for full_sha, data in self._data.items():
            if full_sha.startswith(sha):
                self._alias[sha] = full_sha
                return data

        raise KeyError(__key)

    def __setitem__(self, __key: str, __value: Any) -> None:
        m = regex_sha.fullmatch(__key)
        if not m:
            raise KeyError(__key)

        sha = m.group(1).lower()
        if len(sha) != FULL_LENGTH:
            raise NotImplementedError

        self._data[sha] = __value

    def __delitem__(self, __key: str) -> None:
        raise NotImplementedError


def collect_fields(
    image_ids: Sequence[str], columns: Sequence[str], formats: dict[str, Any] = None
) -> list[dict[str, str]]:
    """Collect image data into dicts."""
    # query once for caching the data in memory
    inspect_image(image_ids)

    # collect field data
    collected = []
    for id_ in image_ids:
        data = {}
        for col in columns:
            data[col] = list(get_field_data(id_, col, formats))
        collected.append(data)

    # explode nested list into multiple rows
    output = []
    for data in collected:
        output.extend(explode_rows(data))
    return output


def explode_rows(source: dict[str, list[Any]]) -> list[dict]:
    """Explodes single object into rows if there are multiple values inside"""
    import itertools

    # categorize
    col_unique = {}
    col_zipped = {}
    for c, v in source.items():
        if not v:
            col_unique[c] = None
        elif len(v) == 1:
            (col_unique[c],) = v
        else:
            col_zipped[c] = v

    # early return
    if not col_zipped:
        yield col_unique
        return

    # explode
    for fv in itertools.zip_longest(*col_zipped.values()):
        row = col_unique.copy()
        for c, v in zip(col_zipped, fv):
            row[c] = v
        yield row


def get_field_data(
    image_id: str, column: str, formats: dict[str, Any] | None = None
) -> Iterator[str]:
    from bollard.utils import (
        format_iso_time,
        format_relative_time,
        format_size,
        split_repo_tag,
    )

    (data,) = inspect_image([image_id])
    formats = formats or {}  # formats could be `None`
    match column:
        case "architecture":
            yield get_architecture(data, formats)
        case "created:iso":
            yield format_iso_time(data["Created"])
        case "created":
            yield format_relative_time(data["Created"])
        case "digest":
            for d in data["RepoDigests"]:
                _, digest = d.split("@", maxsplit=1)
                yield format_digest(digest, formats)
        case "id":
            yield format_digest(data["Id"], formats)
        case "name":
            for s in data["RepoTags"]:
                _, name, _ = split_repo_tag(s)
                yield name
        case "os":
            yield data["Os"]
        case "platform":
            (arch,) = get_field_data(image_id, "architecture", formats)
            (os,) = get_field_data(image_id, "os", formats)
            yield f"{os}/{arch}"
        case "registry":
            for s in data["RepoTags"]:
                registry, _, _ = split_repo_tag(s)
                yield registry
        case "repo_tag":
            for repo, tag in zip(
                get_field_data(image_id, "repository", formats),
                get_field_data(image_id, "tag", formats),
            ):
                yield f"{repo}:{tag}"
        case "repository":
            for s in data["RepoTags"]:
                registry, name, _ = split_repo_tag(s)
                if registry:
                    yield f"{registry}/{name}"
                else:
                    yield name
        case "size":
            yield format_size(data["Size"])
        case "tag":
            for s in data["RepoTags"]:
                _, _, tag = split_repo_tag(s)
                yield tag
        case _:
            logger.critical("Internal error - Unmapped column %s", column)


def get_architecture(data: dict[str, str], formats: dict[str, Any]) -> str:
    import platform
    from gettext import gettext as t

    out = arch = data.get("Architecture", t("unknown"))
    if variant := data.get("Variant"):
        out = f"{arch}/{variant}"

    fmt_highlight = formats.get("highlight_architecture", True)
    if fmt_highlight and platform.machine().upper() != arch.upper():
        out = click.style(out, fg="yellow", bold=True)

    return out


def format_digest(digest: str, formats: dict[str, Any]) -> str:
    import bollard.utils

    short = formats.get("short_digest", True)
    return bollard.utils.format_digest(digest, short)
