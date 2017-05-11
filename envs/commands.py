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


def _get_formulapath(formula):
    return os.path.join(ROOTPATH, formula) + '.yaml'


def _checkpath(formula):
    path = _get_formulapath(formula)
    if not os.path.exists(path):
        _echo('%s does not exist!' % formula)
        sys.exit()


def _readformula(formula):
    formulapath = _get_formulapath(formula)
    with open(formulapath, 'r') as f:
        try:
            formula = yaml.load(f)
        except yaml.ScannerError as e:
            _echo('%s illegal' % formula)
            _echo(e)
            sys.exit()
        else:
            return formula


def _getformulaname(formula):
    name, ext = os.path.splitext(formula)
    return name if ext == '.yaml' else None


def _checkinstall(formula):
    _checkpath(formula)
    formula = _readformula(formula)
    check = formula.get('check', [])
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


def new(formula):
    """TODO: Docstring for new.

    :formula: TODO
    :returns: TODO

    """
    formulapath = _get_formulapath(formula)
    if not os.path.exists(formulapath):
        formula = {}
        formula['name'] = formula
        formula['description'] = formula
        formula['install'] = []
        formula['uninstall'] = []
        with open(formulapath, 'w') as f:
            yaml.dump(formula, f, default_flow_style=False)
    _run('%s %s' % (_geteditor(), formulapath))


def delete(formula):
    """TODO: Docstring for delete.

    :formula: TODO
    :returns: TODO

    """
    _checkpath(formula)
    formulapath = _get_formulapath(formula)
    verify = _confirm('Are you sure you want to delete %s' % formula)
    if not verify:
        return
    os.remove(formulapath)


def show_list():
    """TODO: Docstring for list.
    :returns: TODO

    """
    msg = ''
    for formula in os.listdir(ROOTPATH):
        name = _getformulaname(formula)
        if name:
            msg += '%s\t' % name
    if msg:
        _echo(msg)


def edit(formula):
    """TODO: Docstring for edit.

    :formula: TODO
    :returns: TODO

    """
    new(formula)


def info(formula):
    """TODO: Docstring for info.

    :formula: TODO
    :returns: TODO

    """
    _checkpath(formula)
    formula = _readformula(formula)
    #  TODO: pretty print #
    description = formula.get('description', None)
    if description:
        _echo(description)


def install(formula):
    """TODO: Docstring for install.

    :formula: TODO
    :returns: TODO

    """
    _checkpath(formula)
    formula = _readformula(formula)
    if _checkinstall(formula):
        _echo('%s already installed' % formula)
        sys.exit()
    cmds = formula.get('install', [])
    _run(cmds)


def uninstall(formula):
    """TODO: Docstring for uninstall.

    :formula: TODO
    :returns: TODO

    """
    _checkpath(formula)
    formula = _readformula(formula)
    if not _checkinstall(formula):
        _echo('%s does not installed' % formula)
        sys.exit()
    cmds = formula.get('uninstall', [])
    _run(cmds)


def sync():
    """TODO: Docstring for sync.
    :returns: TODO

    """
    pass
