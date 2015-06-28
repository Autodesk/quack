## Quack - Reuse modules.
Insert specific module from git repository.

#### Features:
* Insert any module from any git repository, as a part of your project.
* Handle dependencies - execute nested quack modules.
* Multiple profiles to deal with different level of complexity.
* Works on UNIX (Mac OS X, Linux); Windows support coming eventually!
* Written entirely in python

#### Examples:
```yaml
name: Quack
description: Quack configuration

modules:
  pyanalytic:
    repository: https://github.com/zonito/PyAnalytics.git
    path: pyanalytics
    branch: master
  subscribe:
    repository: https://github.com/zonito/subscribe.git
    hexsha: 9e3e9642cfea36f4ae216d27df100134920143b9

profiles:
  init:
    tasks: ['modules']
  update:
    tasks: ['modules:subscriibe'] 
    dependencies:
      pyanalytic:
        quack: 'pyanalytic/build.yaml:update'
  clean:
    tasks: ['-modules']
```

#### Installation
There are two ways to install stackit. Both should have roughly the same outcome, but have their advantages/disadvantages.

##### 1) PyPI / pip
This method will always produce some stable build, but may not be the most up to date version. New functionality will come slower than building from this repo.
```shell
$ pip install quack
```

Note, depending on your computer's settings, you may need to `sudo pip install quack`.

##### 2) Build from this repo
This method will always include the latest features, but sometimes will not work at all. Oops!

Clone the repo, then use setup.py to install the package. Note, this process will differ only slightly in a non-bash shell.
```fish
$ git clone https://github.com/zonito/quack.git
$ cd quack
$ python setup.py install
```
Note, depending on your computer's settings, you may need to `sudo python setup.py install`.
