from typing import Sequence

COLUMN_DISPLAY_FORMAT = {
    "architecture": {"title": "ARCH"},
    "created:iso": {"title": "CREATED TIME", "align": "right"},
    "created": {"title": "CREATED", "align": "right"},
    "digest": {"title": "DIGEST"},
    "id": {"title": "ID"},
    "name": {"title": "NAME"},
    "os": {"title": "OS"},
    "platform": {"title": "PLATFORM"},
    "registry": {"title": "REGISTRY"},
    "repo_tag": {"title": "REPO TAG"},
    "repository": {"title": "REPOSITORY"},
    "size": {"title": "SIZE", "align": "right"},
    "tag": {"title": "TAG"},
}


def print_table(columns: Sequence[str], data: list[dict]) -> None:
    import click

    from bollard.utils import tabulate

    # build table spec
    table_spec = {}
    for col in columns:
        table_spec[col] = COLUMN_DISPLAY_FORMAT[col]

    # build table and print
    table = tabulate(table_spec, data)
    click.echo(table)
