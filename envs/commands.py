import os
import subprocess
import shutil

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


def get_packagepath(package):
    return os.path.join(ROOTPATH, package)


def get_configpath(package):
    return os.path.join(get_packagepath(package), package + '.py')


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
    os.makedirs(get_packagepath(package), exist_ok=True)
    templatepath = os.path.abspath(__file__)
    templatepath = os.path.dirname(templatepath)
    templatepath = os.path.join(templatepath, 'template.py')
    configpath = get_configpath(package)
    runshell('cp %s %s' % (templatepath, configpath))
    runshell('%s %s' % (geteditor(), configpath))


def delete(package):
    """TODO: Docstring for delete.

    :package: TODO
    :returns: TODO

    """
    packagepath = get_packagepath(package)
    if not os.path.exists(packagepath):
        echo('%s does not exist!' % package)
        return
    verify = confirm('Are you sure you want to delete %s' % package)
    if not verify:
        return
    shutil.rmtree(packagepath)


def list():
    """TODO: Docstring for list.
    :returns: TODO

    """
    msg = ''
    for package in os.listdir(ROOTPATH):
        msg += '%s\t' % package
    echo(msg)


def edit(package):
    """TODO: Docstring for edit.

    :package: TODO
    :returns: TODO

    """
    new(package)


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


def info(package):
    """TODO: Docstring for info.

    :package: TODO
    :returns: TODO

    """
    pass
