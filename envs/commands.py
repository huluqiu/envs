import os
import subprocess
import sys
import shutil
import configparser
if sys.version_info.major == 3:
    from .packages import yaml3 as yaml
else:
    from .packages import yaml2 as yaml

HOME = os.getenv('HOME')
EDITOR = os.getenv('EDITOR')
CONFIGPATH = os.path.join(HOME, '.envs.conf')
DEFAULTCONFIG = {
    'core': {
        'formulalib': os.path.join(HOME, '.envs/formulas'),
        'syncfile': os.path.join(HOME, '.envs/envs.sync'),
    }
}


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


def _absolutepath(path):
    """convert path such as '~/.envs' to '/Users/username/.envs'

    :path: TODO
    :returns: TODO

    """
    if path.startswith('~'):
        path = path.replace('~', HOME)
    return path


def _readconfig():
    if not os.path.exists(CONFIGPATH):
        _run('touch %s' % CONFIGPATH)
    config = configparser.ConfigParser()
    config.read(CONFIGPATH)
    return config


def _writeconfig(section, key, value):
    config = _readconfig()
    if section not in config.sections():
        config[section] = {}
    config[section][key] = value
    with open(CONFIGPATH, 'w') as f:
        config.write(f)


def _iteminconfig(item):
    """TODO: Docstring for _iteminconfig.

    :item: 'section.key'
    :returns: (section, key) when exists; None when not exists

    """
    status = True
    try:
        section, key = item.split('.')
    except ValueError:
        status = False
    else:
        if section not in DEFAULTCONFIG.keys():
            status = False
        else:
            if key not in DEFAULTCONFIG[section].keys():
                status = False
    return (section, key) if status else None


def _formulalib():
    config = _readconfig()
    section, key = _iteminconfig('core.formulalib')
    default = DEFAULTCONFIG['core']['formulalib']
    formulalib = config.get(section, key, fallback=default)
    formulalib = _absolutepath(formulalib)
    if not os.path.exists(formulalib):
        os.makedirs(formulalib, exist_ok=True)
    return formulalib


def _get_formulapath(formula):
    return os.path.join(_formulalib(), formula) + '.yaml'


def _readformula(formulapath):
    with open(formulapath, 'r') as f:
        try:
            formuladic = yaml.load(f)
        except yaml.ScannerError as e:
            _echo(e)
        else:
            return formuladic


def _getformulaname(filename):
    name, ext = os.path.splitext(filename)
    return name if ext == '.yaml' else None


def _checkinstall(formuladic):
    check = formuladic.get('check', [])
    rs = False
    for con in check:
        if con.find('/') == -1:
            # cmd
            con = shutil.which(con)
        con = _absolutepath(con)
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
        formuladic = {}
        formuladic['description'] = formula
        formuladic['install'] = []
        formuladic['uninstall'] = []
        with open(formulapath, 'w') as f:
            yaml.dump(formuladic, f, default_flow_style=False)
    _run('%s %s' % (EDITOR, formulapath))


def delete(formula):
    """TODO: Docstring for delete.

    :formula: TODO
    :returns: TODO

    """
    formulapath = _get_formulapath(formula)
    if not os.path.exists(formulapath):
        _echo('%s does not exist!' % formula)
    else:
        verify = _confirm('Are you sure you want to delete %s' % formula)
        if verify:
            os.remove(formulapath)


def show_list():
    """TODO: Docstring for list.
    :returns: TODO

    """
    msg = ''
    for formula in os.listdir(_formulalib()):
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
    formulapath = _get_formulapath(formula)
    if not os.path.exists(formulapath):
        _echo('%s does not exist!' % formula)
    else:
        formuladic = _readformula(formulapath)
        if formuladic:
            #  TODO: pretty print #
            description = formuladic.get('description', None)
            if description:
                _echo(description)


def install(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if formuladic:
                if _checkinstall(formuladic):
                    _echo('%s already installed' % formula)
                else:
                    cmds = formuladic.get('install', [])
                    _run(cmds)


def uninstall(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if formuladic:
                if not _checkinstall(formuladic):
                    _echo('%s does not installed' % formula)
                else:
                    cmds = formuladic.get('uninstall', [])
                    _run(cmds)


def config(**kwargs):
    if kwargs['l']:
        _run('cat %s' % CONFIGPATH)
    else:
        _run('%s %s' % (EDITOR, CONFIGPATH))


def sync():
    """TODO: Docstring for sync.
    :returns: TODO

    """
    pass
