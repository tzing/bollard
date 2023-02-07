import bollard.image.ls
from bollard.core import main as _main
from bollard.image.base import group

# unwrapped targets
group.add_unwrapped_targets(
    [
        # fmt: off
        ("build", "Build an image from a Dockerfile"),
        ("history", "Show the history of an image"),
        ("import", "Import the contents from a tarball to create a filesystem image"),
        ("inspect", "Display detailed information on one or more images"),
        ("load", "Load an image from a tar archive or STDIN"),
        ("ls", "List images"),
        ("prune", "Remove unused images"),
        ("pull", "Pull an image or a repository from a registry"),
        ("push", "Push an image or a repository to a registry"),
        ("rm", "Remove one or more images"),
        ("save", "Save one or more images to a tar archive (streamed to STDOUT by default)"),
        ("tag", "Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE"),
        # fmt: on
    ]
)

# aliases
_main.add_alias("images", ["image", "ls"])
