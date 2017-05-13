import sys
from collections import OrderedDict
import subprocess
import os

if sys.version_info.major == 3:
    from .packages import yaml3 as yaml
else:
    from .packages import yaml2 as yaml


def _represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, _represent_ordereddict)


def yamlload(path):
    with open(path, 'r') as f:
        try:
            d = yaml.load(f)
        except Exception as e:
            raise e
    return d


def yamldump(d, path):
    """yaml dump

    :d: dict
    :path: file path(absolute)

    """
    d = OrderedDict(d)
    with open(path, 'w') as f:
        yaml.dump(d, f, default_flow_style=False)


def runshell(cmds):
    if not isinstance(cmds, list):
        cmds = [cmds]
    for cmd in cmds:
        subprocess.run(cmd, shell=True)


def absolutepath(path):
    """convert path such as '~/.envs' to '/Users/username/.envs'

    :path: TODO
    :returns: TODO

    """
    homepath = os.getenv('HOME')
    if path.startswith('~'):
        path = path.replace('~', homepath)
    return path
