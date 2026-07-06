load("@pyoxidizer//pyoxidizer:python.bzl", "default_python_distribution")

# PyOxidizer configuration for the GarutVON Desktop client.
# This package builds the `garutvon.desktop.run` entrypoint as a standalone binary.

def make_exe():
    dist = default_python_distribution()
    exe = dist.to_python_executable("garutvon-desktop")

    # Include the local GarutVON package source.
    for resource in exe.read_package_root("garutvon", ["garutvon"]):
        exe.add_python_resource(resource)

    # Install runtime dependencies required by the desktop client.
    for resource in exe.pip_install(["httpx"]):
        exe.add_python_resource(resource)

    exe.python_config.run_command = "import garutvon.desktop.run as app; app.main()"
    exe.windows_subsystem = "windows"
    return exe
