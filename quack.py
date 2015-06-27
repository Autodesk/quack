#!/usr/bin/env python

import os
import subprocess


def _create_dir(directory, is_fresh=False):
    """Create directory."""
    if os.path.exists(directory) and is_fresh:
        shutil.rmtree(directory)
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

_CONFIG = _get_config()
if _CONFIG:
    _MODULES = '.quack/modules'
    _create_dir(_MODULES)
    for module in _CONFIG.get('modules').items():
        import shutil
        if os.path.exists(module[0]):
            shutil.rmtree(module[0])
        command = 'git submodule add --force %s %s/%s' % (
            module[1]['repository'], _MODULES, module[0])
        print command
        os.popen(command)
        # print command, module
        path = module[1].get('path', '')
        from_path = '%s/%s/%s' % (_MODULES, module[0], path)
        # print path, from_path
        if (path and os.path.exists(from_path)) or not path:
            shutil.copytree(from_path, module[0])
        os.popen('git submodule deinit -f %s/%s' % (_MODULES, module[0]))
        os.popen('git rm --cached %s/%s' % (_MODULES, module[0]))
    os.popen('rm .gitmodules')
    os.popen('git rm --cached .gitmodules')
