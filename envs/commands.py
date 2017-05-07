import os
import subprocess

HOME = os.environ.get('HOME')
ROOTPATH = os.path.join(HOME, '.envs')


def error(msg):
    print('error: %s', msg)


def prompt(msg):
    print('prompt: %s', msg)


def comfirm(msg):
    return True


def geteditor():
    return os.getenv('EDITOR')


def runshell(cmd):
    """TODO: Docstring for runshell.

    :shell: TODO
    :returns: TODO

    """
    subprocess.run(cmd, shell=True)


def new(package):
    """TODO: Docstring for new.

    :package: TODO
    :returns: TODO

    """
    path = os.path.join(ROOTPATH, package)
    os.makedirs(path, exist_ok=True)
    templatepath = os.path.abspath(__file__)
    templatepath = os.path.dirname(templatepath)
    templatepath = os.path.join(templatepath, 'template.py')
    configpath = os.path.join(path, package + '.py')
    runshell('cp %s %s' % (templatepath, configpath))
    runshell('%s %s' % (geteditor(), configpath))


def delete(package):
    """TODO: Docstring for delete.

    :package: TODO
    :returns: TODO

    """
    print('delete %s' % package)


def install(package):
    """TODO: Docstring for install.

    :package: TODO
    :returns: TODO

    """
    pass


def uninstall(package):
    """TODO: Docstring for uninstall.

    :package: TODO
    :returns: TODO

    """
    pass


def sync():
    """TODO: Docstring for sync.
    :returns: TODO

    """
    pass


def edit(package):
    """TODO: Docstring for edit.

    :package: TODO
    :returns: TODO

    """
    pass


def list():
    """TODO: Docstring for list.
    :returns: TODO

    """
    pass


def info(package):
    """TODO: Docstring for info.

    :package: TODO
    :returns: TODO

    """
    pass
