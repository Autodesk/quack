#!/usr/bin/env python

import os
import subprocess
import shutil


def _remove_dir(directory):
    """Remove directory."""
    if os.path.exists(directory):
        shutil.rmtree(directory)


def _create_dir(directory):
    """Create directory."""
    if not os.path.exists(directory):
        os.makedirs(directory)
_create_dir('.quack')

try:
    import yaml
except ImportError as import_error:
    IS_PIP_INSTALLED = '<command>' in os.popen('pip').read()
    if not IS_PIP_INSTALLED:
        from urllib2 import urlopen
        _URL = ('https://raw.githubusercontent.com/pypa/'
                'pip/master/contrib/get-pip.py')
        _FP = urlopen(_URL)
        # Open our local file for writing
        with open('.quack/' + os.path.basename(_URL), "wb") as local_file:
            local_file.write(_FP.read())
        subprocess.call('python .quack/get-pip.py')
        subprocess.call('rm .quack/get-pip.py')
    subprocess.call('pip install pyyaml'.split())
    import yaml


def _get_config():
    """Return yaml configuration."""
    # Make it executable from : http://stackoverflow.com/questions/15587877/
    with open('quack.yaml') as file_pointer:
        return yaml.load(file_pointer)
    return {}


def _fetch_modules():
    """Fetch git submodules."""
    _modules = '.quack/modules'
    _remove_dir('.git/modules/.quack')
    ignore_list = []
    _create_dir(_modules)
    with open('.gitignore', 'r') as file_pointer:
        ignore_list = list(set(file_pointer.read().split('\n')))
    for module in _CONFIG.get('modules').items():
        _remove_dir(module[0])
        command = 'git submodule add --force %s %s/%s' % (
            module[1]['repository'], _modules, module[0])
        print '--> ' + command
        os.popen(command)
        # print command, module
        path = module[1].get('path', '')
        from_path = '%s/%s/%s' % (_modules, module[0], path)
        # print path, from_path
        if (path and os.path.exists(from_path)) or not path:
            shutil.copytree(from_path, module[0])
            os.popen('git submodule deinit -f %s/%s' % (_modules, module[0]))
            os.popen('git rm --cached %s/%s' % (_modules, module[0]))
            os.popen('git rm --cached .gitmodules')
            os.popen('rm .gitmodules')
            with open('.gitignore', 'a') as file_pointer:
                if module[0] not in ignore_list:
                    file_pointer.write('\n' + module[0])
                    ignore_list.append(module[0])

_CONFIG = _get_config()
if _CONFIG:
    _fetch_modules()
