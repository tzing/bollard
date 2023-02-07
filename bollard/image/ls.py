import itertools
import logging
import sys
from typing import Any, Iterator, NoReturn, Sequence

import click

from bollard.image.base import group
from bollard.utils import append_parameters, is_docker_ready, rebuild_args, run_docker

_COLUMNS = {
    # choice: output header, output align
    "architecture": ("ARCH", "left"),
    "created:iso": ("CREATED TIME", "right"),
    "created": ("CREATED", "right"),
    "digest": ("DIGEST", "left"),
    "id": ("ID", "left"),
    "name": ("NAME", "left"),
    "os": ("OS", "left"),
    "platform": ("PLATFORM", "left"),
    "registry": ("REGISTRY", "left"),
    "repo_tag": ("REPO TAG", "left"),
    "repository": ("REPOSITORY", "left"),
    "size": ("SIZE", "right"),
    "tag": ("TAG", "left"),
}

_COLUMN_ALIAS = {
    "arch": "architecture",
    "repo": "repository",
}

_COLUMN_SET = {
    "default": ("id", "repository", "tag", "created", "size"),
    "compact": ("id", "repo_tag"),
}

_COLUMN_CHOICES = sorted(list(_COLUMNS) + list(_COLUMN_ALIAS) + list(_COLUMN_SET))

logger = logging.getLogger(__name__)


class OrderByField(click.Choice):
    def __init__(self, choices: Sequence[str], case_sensitive: bool = True) -> None:
        choices_with_desc = itertools.chain(*((c, f"-{c}") for c in choices))
        super().__init__(list(choices_with_desc), case_sensitive)

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> tuple[bool, str]:
        v: str | None = super().convert(value, param, ctx)
        if not v:
            return None
        elif v.startswith("-"):
            return True, v[1:]
        else:
            return False, v


@group.command(name="ls")
@click.argument("selector", nargs=-1)
@click.option(
    "-C",
    "--column",
    type=click.Choice(_COLUMN_CHOICES, False),
    metavar="COLUMN",
    multiple=True,
    help="Show column (multiple)",
)
@click.option(
    "--order-by",
    type=OrderByField(_COLUMN_CHOICES, False),
    metavar="COLUMN",
    help="Order the output by the column. "
    "Default in ascending, add minus as prefix for decending order",
)
def list_images(
    selector: Sequence[str],
    column: Sequence[str],
    order_by: tuple[bool, str] | None,
    **extra,
):
    """List images

    \b
    ---------
    Selectors
    ---------

    Bollard provides a feature called 'selector'. Selector is like a simple
    alternative to ``--filter`` in docker.

    Selector could be:

    \b
       Pattern
          Pattern is used to match repository name and tag. Wildcard globing is
          supported. e.g. to match image ``public.ecr.aws/nginx/nginx:stable``
          we could use ``public.ecr.aws/*``, ``nginx`` and ``:stable``.
       Hex value
          Hex value would be used to match image ids and the digests.
       Top N Rows
           Specify ``~n`` for selecting top N rows.

    When multiple selector are given, it returns the result of the intersection
    ('AND' operation).

    \b
    -------
    Columns
    -------

    You can select the desired columns to display:

    \b
       architecture (arch)
          Architecture for this image
       created:iso
          Image created time in ISO format (e.g. `2023-01-02T03:04:05+06:00`)
       created
          Relative time of image creation. Similar to docker's default (e.g. `3 days ago`)
       digest
          Image digest(s)
       id
          Image id
       name
          Image name. Extracted from last component in repository name
       os
          Operation system for this image
       platform
          OS and architecture information
       registry
          Registry URI. Extracted from repository name
       repo_tag
          Repository name and tag (e.g. `nginx:stable`)
       repository (repo)
          Repository name
       size
          Image size
       tag
          Image tag

    Also there are some keywords that would be exploded into multiple columns:

    \b
       default
          Converts to id, repository, tag, created and size.
          This is the default layout of native docker command.
       compact
          Converts to id and repo_tag
    """
    # check input & env
    if selector and extra.get("format"):
        logger.error("Selector are not supported to use with format")
        sys.exit(1)
    if not is_docker_ready():
        sys.exit(1)

    # preserve docker's behavior
    if extra.get("format"):
        list_images_fallback(extra)

    # pop top-n arg from selectors
    selectors, top_n = parse_top_n_arg(selector)

    # select images
    image_ids = select_images(
        selectors=selectors,
        incl_interm_img=extra.get("all"),
        filters=extra.get("filter"),
    )

    # build output
    columns = get_columns(
        column,
        flag_digest=extra.get("digests"),
        flag_format=extra.get("format"),
        flag_quiet=extra.get("quiet"),
    )

    data = collect_fields(image_ids, columns, use_full_digest=extra.get("no_trunc"))
    data = explode_dict(data)

    if order_by:
        desc, key = order_by
        if key in columns:
            data = order_dict(data, key, desc)
        else:
            logger.warning(
                "`--order-by` field (%s) not in selected columns (%s). Discard this setting.",
                key,
                ", ".join(columns),
            )

    if top_n > 0:
        data = data[:top_n]

    print_table(columns, data)


group.add_alias("list", ["ls"])


_DOCKER_OPTIONS = [
    click.Option(["-a", "--all"], is_flag=True, help="Show intermediate images"),
    click.Option(["--digests"], is_flag=True, help="Show digests"),
    click.Option(
        ["-f", "--filter"],
        multiple=True,
        help="Filter output based on conditions provided",
    ),
    click.Option(["--format"], help="Pretty-print images using a Go template"),
    click.Option(["--no-trunc"], is_flag=True, help="Don't truncate output"),
    click.Option(["-q", "--quiet"], is_flag=True, help="Only show image IDs"),
]
append_parameters(list_images, _DOCKER_OPTIONS)


def get_columns(
    columns: Sequence[str],
    *,
    flag_digest: bool = False,
    flag_format: bool = False,
    flag_quiet: bool = False,
):
    """Check input and return column list"""
    if flag_format and columns:
        logger.warning("`--format` overrides `--column` settings")
    if flag_digest and columns:
        logger.info(
            "`--digests` is the compatible option for docker. "
            "Suggest to use `--column digest`"
        )
    if flag_quiet and columns:
        logger.warning("`--quiet` overrides `--column` settings")
    if flag_quiet and flag_digest:
        logger.warning("`--quiet` overrides `--digests` setting")

    columns = list(columns) or ["default"]
    if flag_digest:
        columns = list(columns) + ["digest"]
    if flag_quiet:
        columns = ["id"]

    return norm_columns(columns)


def norm_columns(columns: Sequence[str]) -> list[str]:
    """Normalize selected column parameters"""
    norm_columns = []
    for col in columns:
        if col_set := _COLUMN_SET.get(col):
            norm_columns.extend(col_set)
            continue

        if alias_to := _COLUMN_ALIAS.get(col):
            col = alias_to
        if col not in norm_columns:
            norm_columns.append(col)

    return norm_columns


def list_images_fallback(values: dict) -> NoReturn:
    """Run docker command and exit"""
    args = ["image", "ls"]
    args.extend(rebuild_args(values, _DOCKER_OPTIONS))
    rv = run_docker(args)
    sys.exit(rv.returncode)


def select_images(
    selectors: Sequence[str], incl_interm_img: bool, filters: Sequence[str]
) -> list[str]:
    from bollard.image.data import inspect_image, list_image_ids
    from bollard.image.selector import is_image_match_selector

    # get all image list
    if filters:
        image_ids = list_image_ids(incl_interm_img=incl_interm_img, filters=filters)
    else:
        image_ids = list_image_ids(incl_interm_img=incl_interm_img)

    # apply selectors
    if selectors:
        selected = []
        for data in inspect_image(image_ids):
            is_match = True
            for selector in selectors:
                if not is_image_match_selector(data, selector):
                    is_match = False
                    break
            if is_match:
                selected.append(data["Id"])
        image_ids = selected

    return image_ids


def explode_dict(compressed_dict: list[dict]) -> list[dict[str, str]]:
    output = []
    for data in compressed_dict:
        # categorize
        col_unique = {}
        col_zipped = {}
        for c, v in data.items():
            if not v:
                col_unique[c] = None
            elif len(v) == 1:
                (col_unique[c],) = v
            else:
                col_zipped[c] = v

        # explode
        if col_zipped:
            for fv in itertools.zip_longest(*col_zipped.values()):
                d = col_unique.copy()
                for c, v in zip(col_zipped, fv):
                    d[c] = v
                output.append(d)
        else:
            output.append(col_unique)

    return output


def parse_top_n_arg(selectors: Sequence[str]) -> tuple[Sequence[str], int]:
    """Parse the `~n` argument, remove it from selectors."""
    import re

    regex_top_n = re.compile(r"~(\d+)")

    remain = []
    top_n = -1
    for selector in selectors:
        if m := regex_top_n.fullmatch(selector):
            top_n = int(m.group(1))
        else:
            remain.append(selector)

    return remain, top_n


def order_dict(data: list[dict], column: str, desc: bool) -> list[str]:
    def _get_key(d: dict):
        nonlocal column
        v = d[column]
        if v:
            return (desc, v)
        else:
            return (not desc, v)

    return sorted(data, key=_get_key, reverse=desc)


def print_table(column: Sequence[str], data: list[dict]):
    import tabulate

    # build header
    headers = []
    colalign = []
    for c in column:
        text, align = _COLUMNS[c]
        headers.append(click.style(text, bold=True))
        colalign.append(align)

    # build rows
    empty_marker = click.style("-", fg="white", dim=True)
    rows = []
    for d in data:
        rows.append([(d[c] or empty_marker) for c in column])

    if not rows:
        row_empty = [None] * len(column)
        row_empty[0] = click.style("no data", fg="yellow", dim=True)
        rows = [row_empty]

    # print
    table = tabulate.tabulate(
        tablefmt="plain",
        headers=headers,
        colalign=colalign,
        tabular_data=rows,
    )
    click.echo(table)
