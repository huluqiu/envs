import os
import subprocess
import sys
import yaml

HOME = os.environ.get('HOME')
ROOTPATH = os.path.join(HOME, '.envs')


def runshell(cmd):
    subprocess.run(cmd, shell=True)


def run(cmds):
    if isinstance(cmds, list):
        for c in cmds:
            runshell(c)
    else:
        runshell(cmds)


def echo(msg, **kwargs):
    print(msg, **kwargs)


def error(msg):
    echo('error: %s' % msg)


def confirm(msg):
    echo('%s?(y/n)' % msg, end='')
    verify = input()
    return True if verify == 'y' else False


def geteditor():
    return os.getenv('EDITOR')


def get_pokepath(poke):
    return os.path.join(ROOTPATH, poke) + '.yaml'


def checkpath(poke):
    path = get_pokepath(poke)
    if not os.path.exists(path):
        echo('%s does not exist!' % poke)
        sys.exit()


def getconfig(poke):
    pokepath = get_pokepath(poke)
    with open(pokepath, 'r') as f:
        try:
            config = yaml.load(f)
        except yaml.ScannerError as e:
            echo('%s illegal' % poke)
            echo(e)
            sys.exit()
        else:
            return config


def getpokename(poke):
    name, ext = os.path.splitext(poke)
    return name if ext == '.yaml' else None


def new(poke):
    """TODO: Docstring for new.

    :poke: TODO
    :returns: TODO

    """
    pokepath = get_pokepath(poke)
    if not os.path.exists(pokepath):
        config = {}
        config['description'] = poke
        config['install'] = []
        config['uninstall'] = []
        with open(pokepath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    run('%s %s' % (geteditor(), pokepath))


def delete(poke):
    """TODO: Docstring for delete.

    :poke: TODO
    :returns: TODO

    """
    checkpath(poke)
    pokepath = get_pokepath(poke)
    verify = confirm('Are you sure you want to delete %s' % poke)
    if not verify:
        return
    os.remove(pokepath)


def show_list():
    """TODO: Docstring for list.
    :returns: TODO

    """
    msg = ''
    for poke in os.listdir(ROOTPATH):
        name = getpokename(poke)
        if name:
            msg += '%s\t' % name
    if msg:
        echo(msg)


def edit(poke):
    """TODO: Docstring for edit.

    :poke: TODO
    :returns: TODO

    """
    new(poke)


def info(poke):
    """TODO: Docstring for info.

    :poke: TODO
    :returns: TODO

    """
    checkpath(poke)
    config = getconfig(poke)
    #  TODO: pretty print #
    description = config.get('description', None)
    if description:
        echo(description)


def install(poke):
    """TODO: Docstring for install.

    :poke: TODO
    :returns: TODO

    """
    checkpath(poke)
    config = getconfig(poke)
    cmds = config.get('install', [])
    run(cmds)


def uninstall(poke):
    """TODO: Docstring for uninstall.

    :poke: TODO
    :returns: TODO

    """
    checkpath(poke)
    config = getconfig(poke)
    cmds = config.get('uninstall', [])
    run(cmds)


def sync():
    """TODO: Docstring for sync.
    :returns: TODO

    """
    pass
