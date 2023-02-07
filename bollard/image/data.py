import logging
from typing import Any, Iterator, Sequence

import click

from bollard.utils import check_docker_output

logger = logging.getLogger(__name__)

__cache_image_data = {}


def list_image_ids(incl_interm_img: bool = False, filters: list[str] = ()) -> list[str]:
    args = ["images", "--quiet", "--no-trunc"]
    if incl_interm_img:
        args += ["--all"]
    for f in filters:
        args += ["--filter", f]
    data_bytes = check_docker_output(args, use_context=False)
    data_str = data_bytes.rstrip().decode()
    return data_str.splitlines()


def inspect_image(image_ids: list[str]) -> list[dict[str, Any]]:
    """Wrap `docker inspect` command and cache the result."""
    global __cache_image_data
    import json

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

    # review
    request_ids = set(image_ids)
    output_ids = set(d["Id"] for d in output)
    if request_ids != output_ids:
        missing_ids = request_ids - output_ids
        for id_ in missing_ids:
            logger.warning("No such image: %s", id_)

    return output


def get_field_data(
    image_id: str, column: str, formats: dict[str, Any]
) -> Iterator[str]:
    from bollard.utils import (
        format_iso_time,
        format_relative_time,
        format_size,
        split_repo_tag,
    )

    (data,) = inspect_image([image_id])
    match column:
        case "architecture":
            yield format_architecture(data["Architecture"], formats)
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


def format_architecture(arch: str, formats: dict[str, Any]) -> str:
    import platform

    do = formats.get("highlight_architecture", True)
    if not do or platform.machine().upper() == arch.upper():
        return arch
    return click.style(arch, fg="yellow", bold=True)


def format_digest(digest: str, formats: dict[str, Any]) -> str:
    import bollard.utils

    short = formats.get("short_digest", True)
    return bollard.utils.format_digest(digest, short)
