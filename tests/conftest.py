import pytest
from bs4 import BeautifulSoup
from pathlib import Path

DASHBOARD = Path(__file__).parent.parent / "dashboard.html"


@pytest.fixture(scope="session")
def soup():
    return BeautifulSoup(DASHBOARD.read_text(), "lxml")
