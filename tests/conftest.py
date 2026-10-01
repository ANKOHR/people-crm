import pytest
from people_crm.fixtures import generate


@pytest.fixture
def fixture_dir(tmp_path):
    directory = tmp_path / "inputs"
    generate(directory)
    return directory
