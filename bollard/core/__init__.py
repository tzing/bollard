from bollard.core.group import BollardGroup
from bollard.core.main import main


def create_group(name: str, doc: str) -> BollardGroup:
    """Create a command group under main group."""
    group = BollardGroup(name=name, help=doc)
    main.add_command(group)
    return group


# typing
main: BollardGroup
