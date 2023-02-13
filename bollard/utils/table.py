def tabulate(
    columns: list | dict[str, dict], data: list[dict], show_header: bool = True
):
    from gettext import gettext as t

    import click
    import tabulate

    if not data:
        return click.style(t("No data selected"), fg="yellow", dim=True)

    # get column configs
    headers = []
    colalign = []
    for col in columns:
        title = col
        align = "left"
        if isinstance(columns, dict) and (cfg := columns[col]):
            title = cfg.get("title", col)
            align = cfg.get("align", align)
        headers.append(title)
        colalign.append(align)

    if not show_header:
        headers = ()

    # build rows
    EMPTY_MARKER = click.style("-", fg=238, dim=True)
    rows = []
    for row_data in data:
        row = []
        for col in columns:
            row.append(row_data[col] or EMPTY_MARKER)
        rows.append(row)

    # render table
    return tabulate.tabulate(
        tablefmt="plain",
        headers=headers,
        colalign=colalign,
        tabular_data=rows,
    )
