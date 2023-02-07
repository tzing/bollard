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
    from gettext import ngettext

    # get images
    if selector:
        images = select_images(selector)
    else:
        raise NotImplementedError

    if not images:
        click.echo("No image to be removed")
        sys.exit(0)

    # show image
    click.secho(
        ngettext("Would remove this image:", "Would remove these images:", len(images)),
        fg="red",
        bold=True,
    )

    print(images)  # TODO

    if not yes:
        click.confirm("Proceed", prompt_suffix="? ", abort=True)

    click.echo("Removing...")

    raise NotImplementedError


group.add_alias("remove", ["rm"])
group.add_alias("rmi", ["rm"])


def select_images(selectors: Sequence[str]) -> list[str]:
    from bollard.image.data import get_image_data, get_image_ids
    from bollard.image.selector import is_image_match_selector

    selected = []
    for data in get_image_data(get_image_ids()):
        for selector in selectors:
            if is_image_match_selector(data, selector):
                selected.append(data["Id"])
                break

    return selected
