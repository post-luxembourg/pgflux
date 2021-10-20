import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True, scope="session")
def load_dotenv_fixture():
    load_dotenv(".env")
