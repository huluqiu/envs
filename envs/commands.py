import os
import subprocess
import sys
import shutil
if sys.version_info.major == 3:
    from .packages import yaml3 as yaml
else:
    from .packages import yaml2 as yaml

HOME = os.environ.get('HOME')
ROOTPATH = os.path.join(HOME, '.envs')


def _runshell(cmd):
    subprocess.run(cmd, shell=True)


def _run(cmds):
    if isinstance(cmds, list):
        for c in cmds:
            _runshell(c)
    else:
        _runshell(cmds)


def _echo(msg, **kwargs):
    print(msg, **kwargs)


def _confirm(msg):
    _echo('%s?(y/n)' % msg, end='')
    verify = input()
    return True if verify == 'y' else False


def _geteditor():
    return os.getenv('EDITOR')


def _get_pokepath(poke):
    return os.path.join(ROOTPATH, poke) + '.yaml'


def _checkpath(poke):
    path = _get_pokepath(poke)
    if not os.path.exists(path):
        _echo('%s does not exist!' % poke)
        sys.exit()


def _getconfig(poke):
    pokepath = _get_pokepath(poke)
    with open(pokepath, 'r') as f:
        try:
            config = yaml.load(f)
        except yaml.ScannerError as e:
            _echo('%s illegal' % poke)
            _echo(e)
            sys.exit()
        else:
            return config


def _getpokename(poke):
    name, ext = os.path.splitext(poke)
    return name if ext == '.yaml' else None


def _checkinstall(poke):
    _checkpath(poke)
    config = _getconfig(poke)
    check = config.get('check', [])
    rs = False
    for con in check:
        if con.find('/') == -1:
            # cmd
            con = shutil.which(con)
        if con.startswith('~'):
            con = con.replace('~', HOME)
        rs = os.path.exists(con)
        if not rs:
            return False
    return True


def new(poke):
    """TODO: Docstring for new.

    :poke: TODO
    :returns: TODO

    """
    pokepath = _get_pokepath(poke)
    if not os.path.exists(pokepath):
        config = {}
        config['name'] = poke
        config['description'] = poke
        config['install'] = []
        config['uninstall'] = []
        with open(pokepath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    _run('%s %s' % (_geteditor(), pokepath))


def delete(poke):
    """TODO: Docstring for delete.

    :poke: TODO
    :returns: TODO

    """
    _checkpath(poke)
    pokepath = _get_pokepath(poke)
    verify = _confirm('Are you sure you want to delete %s' % poke)
    if not verify:
        return
    os.remove(pokepath)


def show_list():
    """TODO: Docstring for list.
    :returns: TODO

    """
    msg = ''
    for poke in os.listdir(ROOTPATH):
        name = _getpokename(poke)
        if name:
            msg += '%s\t' % name
    if msg:
        _echo(msg)


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
    _checkpath(poke)
    config = _getconfig(poke)
    #  TODO: pretty print #
    description = config.get('description', None)
    if description:
        _echo(description)


def install(poke):
    """TODO: Docstring for install.

    :poke: TODO
    :returns: TODO

    """
    _checkpath(poke)
    config = _getconfig(poke)
    if _checkinstall(poke):
        _echo('%s already installed' % poke)
        sys.exit()
    cmds = config.get('install', [])
    _run(cmds)


def uninstall(poke):
    """TODO: Docstring for uninstall.

    :poke: TODO
    :returns: TODO

    """
    _checkpath(poke)
    config = _getconfig(poke)
    if not _checkinstall(poke):
        _echo('%s does not installed' % poke)
        sys.exit()
    cmds = config.get('uninstall', [])
    _run(cmds)


def sync():
    """TODO: Docstring for sync.
    :returns: TODO

    """
    pass
