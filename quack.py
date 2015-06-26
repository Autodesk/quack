#!/usr/bin/env python

import os
import subprocess


def _create_dir(directory):
    """Create directory."""
    if not os.path.exists(directory):
        os.makedirs(directory)
_create_dir('.quack')

try:
    import yaml
except ImportError as ie:
    is_pip_installed = '<command>' in os.popen('pip').read()
    if not is_pip_installed:
        from urllib2 import urlopen
        url = ('https://raw.githubusercontent.com/pypa/'
               'pip/master/contrib/get-pip.py')
        fp = urlopen(url)
        # Open our local file for writing
        with open('.quack/' + os.path.basename(url), "wb") as local_file:
            local_file.write(fp.read())
        subprocess.call('python .quack/get-pip.py')
        subprocess.call('rm .quack/get-pip.py')
    subprocess.call('pip install pyyaml'.split())
    import yaml


def _get_config():
    """Return yaml configuration."""
    # Make it executable from : http://stackoverflow.com/questions/15587877/
    with open('quack.yaml') as fp:
        return yaml.load(fp)
    return {}

configs = _get_config()
if configs:
    _modules = '.quack/modules'
    _create_dir(_modules)
    for module in configs.get('modules').items():
        subprocess.call('rm -rf %s' % module[0])
        command = 'git submodule add -f %s %s/%s' % (
            module[1]['repository'], _modules, module[0])
        subprocess.call(
            command, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
        print command, module
        path = module[1].get('path', '')
        from_path = '%s/%s/%s' % (_modules, module[0], path)
        print path, from_path
        import shutil
        if (path and os.path.exists(from_path)) or not path:
            shutil.copytree(from_path, module[0])
