"""Configuration for the pytest test suite."""

import pytest
from markdown import Markdown


@pytest.fixture
def md() -> Markdown:
    """Return a Markdown instance.

    Returns:
        Markdown instance.
    """
    return Markdown(extensions=["pycon"])
