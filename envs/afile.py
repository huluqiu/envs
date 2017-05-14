import os
import sys
from collections import OrderedDict
import configparser
if sys.version_info.major == 3:
    from .packages import yaml3 as yaml
else:
    from .packages import yaml2 as yaml


def absolutepath(path, pwd=None, create=False):
    homepath = os.getenv('HOME')
    if path.startswith('~'):
        path = path.replace('~', homepath)
    elif path.startswith('../') and pwd:
        path = path.replace('..', os.path.dirname(pwd))
    elif path.startswith('./') and pwd:
        path = path.replace('.', pwd)
    elif path == '..':
        path = os.path.dirname(pwd)
    elif path == '.':
        path = pwd
    if create and not os.path.exists(path):
        os.makedirs(path)
    return path


def move(src, dest, exist_ok=False, cover=False):
    if not src or not dest:
        return
    if not os.path.exists(src):
        return
    if os.path.exists(dest):
        if exist_ok:
            return
        if cover:
            os.remove(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    os.rename(src, dest)


def symlink(src, dest):
    if not os.path.exists(src):
        return
    try:
        os.symlink(src, dest)
    except FileNotFoundError:
        pass


def read(path, default=None, ft='', mode='r'):
    if not os.path.exists(path):
        return default
    kwargs = {'mode': mode}
    r = {
        'lines': read_lines,
        'yaml': read_yaml,
    }.get(ft, read_normal)(path, **kwargs)
    return r if r else default


def write(obj, path, ft='', mode='w'):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    f = {
        'lines': write_lines,
        'yaml': write_yaml,
    }.get(ft, write_normal)
    kwargs = {
        'mode': mode
    }
    f(obj, path, **kwargs)


def read_normal(path, **kwargs):
    mode = kwargs['mode']
    with open(path, mode) as f:
        return f.read()


def write_normal(obj, path, **kwargs):
    mode = kwargs['mode']
    with open(path, mode) as f:
        f.write(obj)


def read_lines(path, **kwargs):
    mode = kwargs['mode']
    with open(path, mode) as f:
        return f.readlines()


def write_lines(obj, path, **kwargs):
    mode = kwargs['mode']
    with open(path, mode) as f:
        f.writelines(obj)


def read_yaml(path, **kwargs):
    mode = kwargs['mode']
    with open(path, mode) as f:
        try:
            obj = yaml.load(f)
        except Exception as e:
            pass
        else:
            return obj


def write_yaml(obj, path, **kwargs):
    mode = kwargs['mode']
    with open(path, mode) as f:
        yaml.dump(OrderedDict(obj), f, default_flow_style=False)


def _represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, _represent_ordereddict)
