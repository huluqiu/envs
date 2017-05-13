import os
import subprocess
import shutil
import configparser
from . import tools

HOME = os.getenv('HOME')
EDITOR = os.getenv('EDITOR')
CONFIGPATH = os.path.join(HOME, '.envs.conf')
DEFAULTCONFIG = {
    'core': {
        'formulalib': os.path.join(HOME, '.envs/formulas'),
        'syncfile': os.path.join(HOME, '.envs/envs.sync'),
        'backup': os.path.join(HOME, '.envs/backup'),
        'localsync': os.path.join(HOME, '.envs/envs.local'),
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


def _isitemlegal(item):
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


def _getitem(item, config=_readconfig()):
    section, key = item.split('.')
    default = DEFAULTCONFIG[section][key]
    return config.get(section, key, fallback=default)


def _formulalib():
    formulalib = _getitem('core.formulalib')
    formulalib = _absolutepath(formulalib)
    if not os.path.exists(formulalib):
        os.makedirs(formulalib, exist_ok=True)
    return formulalib


def _backup():
    backup = _getitem('core.backup')
    backup = _absolutepath(backup)
    if not os.path.exists(backup):
        os.makedirs(backup, exist_ok=True)
    return backup


def _get_formulapath(formula):
    return os.path.join(_formulalib(), formula) + '.yaml'


def _readformula(formulapath):
    try:
        formuladic = tools.yamlload(formulapath)
    except Exception as e:
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
        if not con:
            return False
        con = _absolutepath(con)
        rs = os.path.exists(con)
        if not rs:
            return False
    return True


def _needlink(source, target):
    return os.path.exists(source) and not os.path.islink(target)


def _readlinesfromfile(path):
    if not os.path.exists(path):
        _run('touch %s' % path)
    with open(path, 'r') as f:
        lines = f.readlines()
    return lines


def _uniquelist(l):
    n = list(set(l))
    n.sort(l.index)
    return n


def new(formula):
    """TODO: Docstring for new.

    :formula: TODO
    :returns: TODO

    """
    formulapath = _get_formulapath(formula)
    if not os.path.exists(formulapath):
        formuladic = {}
        formuladic['description'] = formula
        formuladic['check'] = []
        formuladic['install'] = []
        formuladic['uninstall'] = []
        formuladic['link'] = []
        tools.yamldump(formuladic, formulapath)
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
                _echo('%s: %s' % (formula, description))
            _echo('installed: %s' % _checkinstall(formuladic))


def link(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if not formuladic:
                return
            links = formuladic.get('link', {})
            for target, source in links.items():
                source = _absolutepath(source)
                target = _absolutepath(target)
                if _needlink(source, target):
                    if os.path.exists(target):
                        backuppath = os.path.join(_backup(), formula)
                        os.makedirs(backuppath, exist_ok=True)
                        backuppath = os.path.join(backuppath, os.path.basename(target))
                        os.rename(target, backuppath)
                    os.symlink(source, target)


def unlink(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if not formuladic:
                return
            links = formuladic.get('link', {})
            for target, _ in links.items():
                target = _absolutepath(target)
                if os.path.islink(target):
                    os.remove(target)


def install(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if not formuladic:
                return
            # run install cmds
            if _checkinstall(formuladic):
                _echo('%s already installed' % formula)
            else:
                cmds = formuladic.get('install', [])
                _run(cmds)
                # link config file
                link(formulas=[formula])
                # write to file
                if _checkinstall(formuladic):
                    with open(_getitem('core.localsync'), 'a') as f:
                        f.write('%s\n' % formula)
                    needsync = kwargs.get('sync', True)
                    if needsync:
                        with open(_getitem('core.syncfile'), 'a') as f:
                            f.write('%s\n' % formula)


def uninstall(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if not formuladic:
                return
            # run uninstall cmds
            if not _checkinstall(formuladic):
                _echo('%s does not installed' % formula)
            else:
                cmds = formuladic.get('uninstall', [])
                _run(cmds)
                # unlink config file
                unlink(formulas=[formula])
                # write to file
                if not _checkinstall(formuladic):
                    localpath = _getitem('core.localsync')
                    formulas_local = _readlinesfromfile(localpath)
                    formulas_local.remove('%s\n' % formula)
                    with open(localpath, 'w') as f:
                        f.writelines(formulas_local)
                    needsync = kwargs.get('sync', True)
                    if needsync:
                        syncpath = _getitem('core.syncfile')
                        formulas_sync = _readlinesfromfile(syncpath)
                        formulas_sync.remove('%s\n' % formula)
                        with open(syncpath, 'w') as f:
                            f.writelines(formulas_sync)


def config(**kwargs):
    if kwargs['l']:
        _run('cat %s' % CONFIGPATH)
    else:
        _run('%s %s' % (EDITOR, CONFIGPATH))


def sync():
    """TODO: Docstring for sync.
    :returns: TODO

    """
    # read syncfile
    syncpath = _getitem('core.syncfile')
    formulas_sync = _readlinesfromfile(syncpath)
    localpath = _getitem('core.localsync')
    formulas_local = _readlinesfromfile(localpath)
    # install or uninstall
    install_formulas = list(set(formulas_sync) - set(formulas_local))
    formulas = map(lambda n: n.replace('\n', ''), install_formulas)
    install(formulas=formulas, sync=False)
    uninstall_formulas = list(set(formulas_local) - set(formulas_sync))
    formulas = map(lambda n: n.replace('\n', ''), uninstall_formulas)
    uninstall(formulas=formulas, sync=False)
    formulas_local = _readlinesfromfile(localpath)
    # check
    if formulas_local == formulas_sync:
        _echo('sync succeed!')
    else:
        _echo('sync failed!')
