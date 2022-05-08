import toml

import chrome_local_storage


with open('pyproject.toml') as project_file:
    project = toml.load(project_file)


def test_version():
    version = project['tool']['poetry']['version']
    assert chrome_local_storage.__version__ == version
