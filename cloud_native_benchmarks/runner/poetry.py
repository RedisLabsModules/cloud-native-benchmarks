#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#
import toml

from cloud_native_benchmarks import __version__


def populate_with_poetry_data():
    project_name = "cnb-run"
    project_version = __version__
    project_description = None
    try:
        poetry_data = toml.load("pyproject.toml")["tool"]["poetry"]
        project_name = poetry_data["name"]
        project_version = poetry_data["version"]
        project_description = poetry_data["description"]
    except FileNotFoundError:
        pass

    return project_name, project_description, project_version


def print_version(project_name, project_version):
    print(
        "{project_name} {project_version}".format(
            project_name=project_name, project_version=project_version
        )
    )
