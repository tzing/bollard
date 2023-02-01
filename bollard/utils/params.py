import typing

if typing.TYPE_CHECKING:
    import click


def rebuild_args(
    values: dict[str, typing.Any], parameters: list["click.Parameter"]
) -> list[str]:
    """Rebuild arguments."""
    args = []

    for option in parameters:
        value = values.get(option.name)
        opt = option.opts[0]
        if option.is_flag and value:
            args += [opt]
        elif option.multiple and value:
            for elem in value:
                args += [opt, str(elem)]
        elif value:
            args += [opt, str(value)]

    return args


def append_parameters(
    cmd: "click.Command", parameters: list["click.Parameter"]
) -> None:
    params = cmd.params + parameters
    params = sorted(params, key=lambda o: o.name)
    cmd.params = params
