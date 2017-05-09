import os
import subprocess
import json

HOME = os.environ.get('HOME')
ROOTPATH = os.path.join(HOME, '.envs')


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
    return os.path.join(ROOTPATH, poke) + '.json'


def runshell(cmd):
    subprocess.run(cmd, shell=True)


def getpokename(poke):
    name, ext = os.path.splitext(poke)
    return name if ext == '.json' else None


def new(poke):
    """TODO: Docstring for new.

    :poke: TODO
    :returns: TODO

    """
    pokepath = get_pokepath(poke)
    if not os.path.exists(pokepath):
        config = {}
        config['description'] = poke
        config['install'] = ''
        config['uninstall'] = ''
        with open(pokepath, 'w') as f:
            f.write(json.dumps(config, indent=2))
    runshell('%s %s' % (geteditor(), pokepath))


def delete(poke):
    """TODO: Docstring for delete.

    :poke: TODO
    :returns: TODO

    """
    pokepath = get_pokepath(poke)
    if not os.path.exists(pokepath):
        echo('%s does not exist!' % poke)
        return
    verify = confirm('Are you sure you want to delete %s' % poke)
    if not verify:
        return
    os.remove(pokepath)


def list():
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


def install(poke):
    """TODO: Docstring for install.

    :poke: TODO
    :returns: TODO

    """
    pass


def uninstall(poke):
    """TODO: Docstring for uninstall.

    :poke: TODO
    :returns: TODO

    """
    pass


def sync():
    """TODO: Docstring for sync.
    :returns: TODO

    """
    pass


def info(poke):
    """TODO: Docstring for info.

    :poke: TODO
    :returns: TODO

    """
    pass
