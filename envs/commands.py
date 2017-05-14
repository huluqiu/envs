import os
import shutil
import configparser
from . import tools
from . import afile

HOME = os.getenv('HOME')
EDITOR = os.getenv('EDITOR')
ZSHRCPATH = os.path.join(HOME, '.zshrc')
ENVSLIB = os.path.join(HOME, '.envs')
ENVS_CONFIG = os.path.join(ENVSLIB, 'envs.conf')
ENVS_ZSHRC = os.path.join(ENVSLIB, 'envs.zshrc')
ENVS_LOCAL = os.path.join(ENVSLIB, 'envs.local')
DEFAULTCONFIG = {
    'user': {
        'formulalib': os.path.join(ENVSLIB, 'formulas'),
        'configlib': os.path.join(ENVSLIB, 'configlib'),
    }
}


def _echo(msg, **kwargs):
    print(msg, **kwargs)


def _confirm(msg):
    _echo('%s?(y/n)' % msg, end='')
    verify = input()
    return True if verify == 'y' else False


def _getitem(item):
    section, key = item.split('.')
    default = DEFAULTCONFIG[section][key]
    config = configparser.ConfigParser()
    if not os.path.exists(ENVS_CONFIG):
        afile.write('', ENVS_CONFIG)
    config.read(ENVS_CONFIG)
    return config.get(section, key, fallback=default)


def _configlib():
    return _getitem('user.configlib')


def _workspace(formula):
    return os.path.join(_configlib(), 'configs', formula)


def _backuppath(formula):
    return os.path.join(ENVSLIB, 'backup', formula)


def _zshrc(workspace):
    return os.path.join(workspace, 'zshrc')


def _sync_file():
    return afile.absolutepath(os.path.join(_configlib(), 'envs.sync'))


def _get_formulapath(formula):
    formulalib = _getitem('user.formulalib')
    p = os.path.join(formulalib, formula) + '.yaml'
    return afile.absolutepath(p)


def _readformula(formula):
    formulapath = _get_formulapath(formula)
    if not os.path.exists(formulapath):
        _echo('%s does not exist!' % formula)
    return afile.read(formulapath, {}, ft='yaml')


def _getformulaname(filename):
    name, ext = os.path.splitext(filename)
    return name if ext == '.yaml' else None


def _checkinstall(formula):
    formuladic = _readformula(formula)
    check = formuladic.get('check', [])
    if check:
        for con in check:
            if con.find('/') == -1:
                # cmd
                con = shutil.which(con)
            if not con:
                return False
            con = afile.absolutepath(con)
            if not os.path.exists(con):
                return False
        return True
    else:
        localpath = os.path.join(ENVSLIB, 'envs.local')
        formulas_local = afile.read(localpath, [], ft='lines')
        content = formula + '\n'
        return content in formulas_local


def new(formula):
    formulapath = _get_formulapath(formula)
    if not os.path.exists(formulapath):
        formuladic = {}
        formuladic['description'] = formula
        formuladic['check'] = []
        formuladic['install'] = []
        formuladic['uninstall'] = []
        formuladic['link'] = []
        afile.write(formuladic, formulapath, ft='yaml')
    tools.runshell('%s %s' % (EDITOR, formulapath))


def delete(formula):
    formulapath = _get_formulapath(formula)
    if not os.path.exists(formulapath):
        _echo('%s does not exist!' % formula)
    else:
        verify = _confirm('Are you sure you want to delete %s' % formula)
        if verify:
            os.remove(formulapath)


def show_list():
    formulalib = _getitem('user.formulalib')
    formulalib = afile.absolutepath(formulalib)
    if os.path.exists(formulalib):
        msg = ''
        for formula in os.listdir(formulalib):
            name = _getformulaname(formula)
            if name:
                msg += '%s\t' % name
        if msg:
            _echo(msg)


def edit(formula):
    new(formula)


def info(formula):
    formuladic = _readformula(formula)
    if formuladic:
        #  TODO: pretty print #
        description = formuladic.get('description', None)
        if description:
            _echo('%s: %s' % (formula, description))
        _echo('installed: %s' % _checkinstall(formula))


def link(**kwargs):
    for formula in kwargs['formulas']:
        formuladic = _readformula(formula)
        if not formuladic:
            return
        if not _checkinstall(formula):
            return
        links = formuladic.get('link')
        if not links:
            return
        workspace = afile.absolutepath(_workspace(formula), create=True)
        for source, target in links.items():
            source = afile.absolutepath(source, pwd=workspace)
            target = afile.absolutepath(target)
            backup = _backuppath(formula)
            backup_from, backup_to = None, None
            migrate_from, migrate_to = None, None
            if (os.path.exists(source) and
                    not os.path.islink(target) and
                    os.path.exists(target)):
                    backup_from = target
                    backup_to = os.path.join(backup, os.path.basename(target))
            elif kwargs['m']:
                if os.path.exists(source):
                    backup_from = source,
                    backup_to = os.path.join(backup, os.path.basename(source))
                if os.path.exists(target):
                    #  TODO: 多级目录 #
                    migrate_from = target
                    migrate_to = source
            afile.move(backup_from, backup_to)
            afile.move(migrate_from, migrate_to)
            afile.symlink(source, target)


def unlink(**kwargs):
    for formula in kwargs['formulas']:
        formuladic = _readformula(formula)
        if formuladic:
            links = formuladic.get('link', {})
            for _, target in links.items():
                target = afile.absolutepath(target)
                if os.path.islink(target):
                    os.remove(target)


def zsh(**kwargs):
    for formula in kwargs['formulas']:
        formuladic = _readformula(formula)
        if not formuladic:
            return
        if not _checkinstall(formula):
            return
        zshconfigs = formuladic.get('zsh')
        if not zshconfigs:
            return
        zshconfigs = list(map(lambda n: n + '\n', zshconfigs))
        workspace = afile.absolutepath(_workspace(formula), create=True)
        zshrc = _zshrc(workspace)
        afile.write(zshconfigs, zshrc, ft='lines')
        content = 'source %s\n' % zshrc
        zshlist = afile.read(ENVS_ZSHRC, [], ft='lines')
        if content not in zshlist:
            zshlist.append(content)
            afile.write(zshlist, ENVS_ZSHRC, ft='lines')


def unzsh(**kwargs):
    for formula in kwargs['formulas']:
        formuladic = _readformula(formula)
        if not formuladic:
            return
        workspace = afile.absolutepath(_workspace(formula), create=True)
        zshrc = _zshrc(workspace)
        content = 'source %s\n' % zshrc
        zshlist = afile.read(ENVS_ZSHRC, [], ft='lines')
        if content in zshlist:
            zshlist.remove(content)
            afile.write(zshlist, ENVS_ZSHRC, ft='lines')


def install(**kwargs):
    for formula in kwargs['formulas']:
        formuladic = _readformula(formula)
        if not formuladic:
            return
        if _checkinstall(formula):
            _echo('%s already installed' % formula)
        else:
            # run install cmds
            cmds = formuladic.get('install', [])
            tools.runshell(cmds)
            # write to sync file
            needcheck = formuladic.get('check', [])
            needwrite = _checkinstall(formula) if needcheck else True
            if needwrite:
                afile.write(formula + '\n', ENVS_LOCAL, mode='a')
                needsync = kwargs.get('sync', True)
                if needsync:
                    afile.write(formula + '\n', _sync_file(), mode='a')
            # link config file
            link(formulas=[formula], m=False)
            # zsh
            zsh(formulas=[formula])


def uninstall(**kwargs):
    for formula in kwargs['formulas']:
        formuladic = _readformula(formula)
        if not formuladic:
            return
        if not _checkinstall(formula):
            _echo('%s does not installed' % formula)
        else:
            # unzsh
            unzsh(formulas=[formula])
            # unlink config file
            unlink(formulas=[formula])
            # run uninstall cmds
            cmds = formuladic.get('uninstall', [])
            tools.runshell(cmds)
            # write to sync file
            needcheck = formuladic.get('check', [])
            needwrite = not _checkinstall(formula) if needcheck else True
            if needwrite:
                formulas_local = afile.read(ENVS_LOCAL, [], ft='lines')
                content = '%s\n' % formula
                if content not in formulas_local:
                    return
                formulas_local.remove(content)
                afile.write(formulas_local, ENVS_LOCAL, ft='lines')
                needsync = kwargs.get('sync', True)
                if needsync:
                    syncpath = _sync_file()
                    formulas_sync = afile.read(syncpath, [], ft='lines')
                    formula = formula + '\n'
                    if formula in formulas_sync:
                        formulas_sync.remove(formula)
                        afile.write(formulas_sync, syncpath, ft='lines')


def config(**kwargs):
    if kwargs['l']:
        tools.runshell('cat %s' % ENVS_CONFIG)
    else:
        tools.runshell('%s %s' % (EDITOR, ENVS_CONFIG))


def sync():
    # read syncfile
    formulas_sync = afile.read(_sync_file(), [], ft='lines')
    formulas_local = afile.read(ENVS_LOCAL, [], ft='lines')
    # install or uninstall
    install_formulas = list(set(formulas_sync) - set(formulas_local))
    formulas = map(lambda n: n.replace('\n', ''), install_formulas)
    install(formulas=formulas, sync=False)
    uninstall_formulas = list(set(formulas_local) - set(formulas_sync))
    formulas = map(lambda n: n.replace('\n', ''), uninstall_formulas)
    uninstall(formulas=formulas, sync=False)
    formulas_local = afile.read(ENVS_LOCAL, [], ft='lines')
    # check
    if formulas_local == formulas_sync:
        _echo('sync succeed!')
    else:
        _echo('sync failed!')


def test():
    pass
