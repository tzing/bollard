import sys
from typing import Sequence

import click

from bollard.image.base import group


@group.command(name="rm")
@click.argument("selector", nargs=-1)
@click.option("-y", "--yes", is_flag=True, help="Proceed deletion without confirm")
def remove_images(selector: Sequence[str], yes: bool, **extra):
    """
    Remove one or more images

    The main arguments are selectors to pick image(s). It could be globing
    pattern on repository registry, name or tag, and hex digest that matches
    image id or digests. When multiple selectors are given, it selects the
    result of the union ('OR' operation).
    """
    from gettext import gettext as t
    from gettext import ngettext

    from bollard.image.data import collect_fields
    from bollard.image.display import print_table

    # get images
    if selector:
        images = select_images(selector)
    else:
        images = interactive_select_image()

    if not images:
        msg = click.style(t("No image to be removed"), fg="yellow", bold=True)
        click.echo(msg, err=True)
        sys.exit(0)

    # show image
    click.secho(
        ngettext("Would remove this image:", "Would remove these images:", len(images)),
        fg="red",
        bold=True,
    )
    click.echo()

    cols = ["id", "repository", "tag"]
    data = collect_fields(images, cols)
    print_table(cols, data)
    click.echo()

    # confirm
    if yes:
        click.echo(t("Removing..."))
    else:
        click.confirm(t("Proceed"), abort=True)

    raise NotImplementedError


group.add_alias("remove", ["rm"])
group.add_alias("rmi", ["rm"])


def select_images(selectors: Sequence[str]) -> list[str]:
    from bollard.image.data import inspect_image, list_image_ids
    from bollard.image.selector import is_image_match_selector

    selected = []
    for data in inspect_image(list_image_ids()):
        for selector in selectors:
            if is_image_match_selector(data, selector):
                selected.append(data["Id"])
                break

    return selected


def interactive_select_image() -> set[str]:
    from gettext import gettext as t

    from bollard.image.data import collect_fields, list_image_ids
    from bollard.image.display import build_table
    from bollard.utils import interactive_select

    COLUMNS = ["id", "size", "created", "repo_tag"]

    # get data
    image_ids = list_image_ids()
    image_data = collect_fields(image_ids, COLUMNS)

    # format into colored table
    last_id = None
    for data in image_data:
        is_duplicated = (id_ := data["id"]) == last_id
        last_id = id_

        data["id"] = click.style(
            data["id"], fg="cyan" if not is_duplicated else "blue", bold=True
        )
        data["size"] = click.style(data["size"], fg="yellow", dim=True)

    head, *rows = build_table(COLUMNS, image_data).splitlines()

    # call fzf
    selected = interactive_select(
        prompt=t("Tab to select images to remove, enter to continue."),
        header=head,
        items=rows,
    )

    # extract id
    output = set()
    for line in selected:
        id_, _ = line.split(maxsplit=1)
        output.add(id_)

    return output
