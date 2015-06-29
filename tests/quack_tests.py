"""Unit tests."""

import os
from quack import quack

# pylint: disable=W0212


def test_create_dir():
    """Directory specific tests."""
    # quack._create_dir('qt')
    # quack._create_dir('qt')
    assert os.path.exists('qt')
    quack._remove_dir('qt')
    quack._remove_dir('qt')
    assert not os.path.exists('qt')
