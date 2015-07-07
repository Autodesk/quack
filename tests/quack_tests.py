"""Unit tests."""
# pylint: disable=W0212

import os
import types
from quack import quack


def test_create_dir():
    """Directory specific tests."""
    quack._create_dir('qt')
    quack._create_dir('qt')
    assert os.path.exists('qt')
    quack._remove_dir('qt')
    quack._remove_dir('qt')
    assert not os.path.exists('qt')


def test_get_config():
    """Test on Get configuration."""
    assert isinstance(quack._get_config(), types.DictionaryType)
