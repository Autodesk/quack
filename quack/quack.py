#!/usr/bin/env python
# pylint: disable=C0325

"""Quack!!"""

import argparse
import git
import os
import shutil
import subprocess
import yaml


_ARGS = None


def _setup():
    """Setup parser if executed script directly."""
    parser = argparse.ArgumentParser(description='Quack builder')
    parser.add_argument(
        '-y', '--yaml', help='Provide custom yaml. default: quack.yaml')
    parser.add_argument(
        '-p', '--profile', help='Run selected profile. default: init',
        nargs='?')
    return parser.parse_args()


def _remove_dir(directory):
    """Remove directory."""
    if os.path.exists(directory):
        shutil.rmtree(directory)
        return True
    return False


def _create_dir(directory):
    """Create directory."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def _get_config():
    """Return yaml configuration."""
    yaml_file = (hasattr(_ARGS, 'yaml') and _ARGS.yaml) or 'quack.yaml'
    if os.path.isfile(yaml_file):
        with open(yaml_file) as file_pointer:
            return yaml.load(file_pointer)
    return


def _fetch_modules(config, specific_module=None):
    """Fetch git submodules."""
    module_list = config.get('modules')
    if not module_list:
        print('No modules found.')
        return
    modules = '.quack/modules'
    ignore_list = []
    _remove_dir('.git/modules/.quack')
    _create_dir(modules)
    if config.get('gitignore') and os.path.isfile('.gitignore'):
        with open('.gitignore', 'r') as file_pointer:
            ignore_list = list(set(file_pointer.read().split('\n')))
    repo = git.Repo('.')
    for module in module_list.items():
        if specific_module and specific_module != module[0]:
            continue
        tag = module[1].get('tag')
        hexsha = module[1].get('hexsha')
        if tag and hexsha:
            print('%s: Cannot be both tag & hexsha.' % module[0])
            continue
        _remove_dir(module[0])
        print('Cloning: ' + module[1]['repository'])
        sub_module = repo.create_submodule(
            module[0], modules + '/' + module[0],
            url=module[1]['repository'],
            branch=module[1].get('branch', 'master')
        )

        if tag:
            subprocess.call(
                ['git', 'checkout', '--quiet', 'tags/' + tag],
                cwd=modules + '/' + module[0])
            tag = ' (' + tag + ') '
        elif hexsha:
            subprocess.call(
                ['git', 'checkout', '--quiet', hexsha],
                cwd=modules + '/' + module[0])
            hexsha = ' (' + hexsha + ')'
        else:
            hexsha = ' (' + sub_module.hexsha + ')'

        path = module[1].get('path', '')
        from_path = '%s/%s/%s' % (modules, module[0], path)
        is_exists = os.path.exists(from_path)
        if (path and is_exists) or not path:
            shutil.copytree(
                from_path, module[0],
                ignore=shutil.ignore_patterns('.git*'))
        elif not is_exists:
            print('%s folder does not exists. Skipped.' % path)

        # Remove submodule.
        sub_module.remove()
        if os.path.isfile('.gitmodules'):
            subprocess.call('rm .gitmodules'.split())
            subprocess.call('git rm --quiet --cached .gitmodules'.split())

        print('\033[1A' + '  Cloned: ' + module[0] + (tag or hexsha))
        print('\033[1A' + '\033[32m' +
              str(u'\u2713'.encode('utf-8')) + '\033[37m')

        if config.get('gitignore'):
            with open('.gitignore', 'a') as file_pointer:
                if module[0] not in ignore_list:
                    file_pointer.write('\n' + module[0])
                    ignore_list.append(module[0])


def _clean_modules(config, specific_module=None):
    """Remove all given modules."""
    for module in config.get('modules').items():
        if specific_module and specific_module != module[0]:
            continue
        if _remove_dir(module[0]):
            print('Cleaned', module[0])


def _run_nested_quack(dependency):
    """Execute all required dependencies."""
    if not dependency or dependency[0] != 'quack':
        return
    quack = dependency[1]
    slash_index = quack.rfind('/')
    command = ['quack']
    module = '.'
    if slash_index > 0:
        module = quack[:slash_index]
    colon_index = quack.find(':')
    if len(quack) > colon_index + 1:
        command.append('-p')
        command.append(quack[colon_index + 1: len(quack)])
    if colon_index > 0:
        command.append('-y')
        command.append(quack[slash_index + 1:colon_index])
    print('Quack..' + module)
    git.Repo.init(module)
    subprocess.call(command, cwd=module)
    _remove_dir(module + '/.git')
    return True


def _run_tasks(config, profile):
    """Run given tasks."""
    dependencies = profile.get('dependencies', {})
    stats = {'tasks': 0, 'dependencies': 0}
    if isinstance(dependencies, dict):
        for dependency in profile.get('dependencies', {}).items():
            _run_nested_quack(dependency)
            stats['dependencies'] += 1
    tasks = profile.get('tasks', [])
    if not tasks:
        print('No tasks found.')
        return stats
    for command in tasks:
        stats['tasks'] += 1
        is_negate = command[0] == '-'
        if is_negate:
            command = command[1:]
        module = None
        is_modules = command.find('modules:') == 0 or 'modules' == command
        is_quack = command.find('quack:') == 0
        is_cmd = command.find('cmd:') == 0

        if is_modules and command != 'modules':
            module = command.replace('modules:', '')
        elif is_quack:
            _run_nested_quack(('quack', command.replace('quack:', '')))
        elif is_cmd:
            cmd = command.replace('cmd:', '')
            subprocess.call(cmd.split())

        if is_modules and not is_negate:
            _fetch_modules(config, module)
        elif is_modules and is_negate:
            _clean_modules(config, module)
    return stats


def _prompt_to_create():
    """Prompt user to create quack configuration."""
    yes_or_no = raw_input(
        'No quack configuration found, do you want to create one? (y/N): ')
    if yes_or_no.lower() == 'y':
        project_name = raw_input('Provide project name: ')
        with open('quack.yaml', 'a') as file_pointer:
            file_pointer.write("""name: %s
modules:
profiles:
  init:
    tasks: ['modules']""" % project_name)
        return _get_config()
    return


def main():
    """Entry point."""
    global _ARGS
    _create_dir('.quack')
    if _ARGS is None:
        _ARGS = _setup()
    config = _get_config()
    if not config:
        config = _prompt_to_create()
        if not config:
            return
    if not _ARGS.profile:
        _ARGS.profile = 'init'
    profile = config.get('profiles', {}).get(_ARGS.profile, {})
    # print(_ARGS.profile, profile)
    stats = _run_tasks(config, profile)
    print('%s task(s) completed with %s dependencies.' % (
        stats['tasks'], stats['dependencies']))

if __name__ == '__main__':
    _ARGS = _setup()
    main()
