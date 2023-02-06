import logging
from typing import Any

from bollard.utils import check_docker_output

logger = logging.getLogger(__name__)

__cache_image_data = {}


def get_image_ids(incl_interm_img: bool = False, filters: list[str] = ()) -> list[str]:
    args = ["images", "--quiet", "--no-trunc"]
    if incl_interm_img:
        args += ["--all"]
    for f in filters:
        args += ["--filter", f]
    data_bytes = check_docker_output(args, use_context=False)
    data_str = data_bytes.rstrip().decode()
    return data_str.splitlines()


def get_image_data(image_ids: list[str]) -> list[dict[str, Any]]:
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
