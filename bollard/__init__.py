__all__ = [
    "__version__",
    "image",
    "main",
    "misc",
]

from . import constants, core, image, misc

__version__ = constants.pkg_version

main = core.main

_SUBCOMMANDS = [
    # a complete command list of docker
    # fmt: off
    ("attach", "Attach local standard input, output, and error streams to a running container"),
    ("build", "Build an image from a Dockerfile"),
    ("builder", "Manage builds"),
    ("buildx", "Docker Buildx"),
    ("commit", "Create a new image from a container's changes"),
    ("compose", "Docker Compose"),
    ("config", "Manage Docker configs"),
    ("container", "Manage containers"),
    ("context", "Manage contexts"),
    ("cp", "Copy files/folders between a container and the local filesystem"),
    ("create", "Create a new container"),
    ("dev", "Docker Dev Environments"),
    ("diff", "Inspect changes to files or directories on a container's filesystem"),
    ("events", "Get real time events from the server"),
    ("exec", "Run a command in a running container"),
    ("export", "Export a container's filesystem as a tar archive"),
    ("extension", "Manages Docker extensions"),
    ("history", "Show the history of an image"),
    ("image", "Manage images"),
    ("images", "List images"),
    ("import", "Import the contents from a tarball to create a filesystem image"),
    ("info", "Display system-wide information"),
    ("inspect", "Return low-level information on Docker objects"),
    ("kill", "Kill one or more running containers"),
    ("load", "Load an image from a tar archive or STDIN"),
    ("login", "Log in to a Docker registry"),
    ("logout", "Log out from a Docker registry"),
    ("logs", "Fetch the logs of a container"),
    ("manifest", "Manage Docker image manifests and manifest lists"),
    ("network", "Manage networks"),
    ("node", "Manage Swarm nodes"),
    ("pause", "Pause all processes within one or more containers"),
    ("plugin", "Manage plugins"),
    ("port", "List port mappings or a specific mapping for the container"),
    ("ps", "List containers"),
    ("pull", "Pull an image or a repository from a registry"),
    ("push", "Push an image or a repository to a registry"),
    ("rename", "Rename a container"),
    ("restart", "Restart one or more containers"),
    ("rm", "Remove one or more containers"),
    ("rmi", "Remove one or more images"),
    ("run", "Run a command in a new container"),
    ("save", "Save one or more images to a tar archive (streamed to STDOUT by default)"),
    ("sbom", "View the packaged-based Software Bill Of Materials (SBOM) for an image"),
    ("scan", "Docker Scan"),
    ("search", "Search the Docker Hub for images"),
    ("secret", "Manage Docker secrets"),
    ("service", "Manage services"),
    ("stack", "Manage Docker stacks"),
    ("start", "Start one or more stopped containers"),
    ("stats", "Display a live stream of container(s) resource usage statistics"),
    ("stop", "Stop one or more running containers"),
    ("swarm", "Manage Swarm"),
    ("system", "Manage Docker"),
    ("tag", "Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE"),
    ("top", "Display the running processes of a container"),
    ("trust", "Manage trust on Docker images"),
    ("unpause", "Unpause all processes within one or more containers"),
    ("update", "Update configuration of one or more containers"),
    ("version", "Show the Docker version information"),
    ("volume", "Manage volumes"),
    ("wait", "Block until one or more containers stop, then print their exit codes"),
    # fmt: on
]

main.add_unwrapped_targets(_SUBCOMMANDS)

# aliases
main.add_alias("containers", ["container", "ls"])
main.add_alias("networks", ["network", "ls"])
main.add_alias("volumes", ["volume", "ls"])
