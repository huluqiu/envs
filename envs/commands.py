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
    if not os.path.exists(formulalib):
        os.mkdir(formulalib)
    return formulalib


def _get_formulapath(formula):
    return os.path.join(_formulalib(), formula) + '.yaml'


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
    if _checkinstall(formula):
        _echo('%s already installed' % formula)
    else:
        formula = _readformula(formula)
        cmds = formula.get('install', [])
        _run(cmds)


def uninstall(formula):
    """TODO: Docstring for uninstall.

    :formula: TODO
    :returns: TODO

    """
    if not _checkinstall(formula):
        _echo('%s does not installed' % formula)
    else:
        formula = _readformula(formula)
        cmds = formula.get('uninstall', [])
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
