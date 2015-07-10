"""Unit tests."""
# pylint: disable=W0212

import os
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
    assert isinstance(quack._get_config(), dict)


def test_run_tasks_cmd():
    """Test on run command task."""
    config = quack._get_config()
    profile = config.get('profiles').get('cmd', {})
    assert quack._run_tasks(config, profile)


def test_run_nested_quack():
    """Test on nested quack."""
    assert quack._run_nested_quack(('quack', 'nested_quack_test'))
