import os
import shutil
import configparser
from . import tools

HOME = os.getenv('HOME')
EDITOR = os.getenv('EDITOR')
CONFIGPATH = os.path.join(HOME, '.envs.conf')
ZSHRCPATH = os.path.join(HOME, '.zshrc')
ENVSLIB = os.path.join(HOME, '.envs')
SYNCFILE = 'envs.sync'
DEFAULTCONFIG = {
    'core': {
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


def _readconfig():
    if not os.path.exists(CONFIGPATH):
        tools.runshell('touch %s' % CONFIGPATH)
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


def _path(item):
    path = _getitem(item)
    path = tools.absolutepath(path)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


def _get_formulapath(formula):
    return os.path.join(_path('core.formulalib'), formula) + '.yaml'


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
    if not check:
        return False
    rs = False
    for con in check:
        if con.find('/') == -1:
            # cmd
            con = shutil.which(con)
        if not con:
            return False
        con = tools.absolutepath(con)
        rs = os.path.exists(con)
        if not rs:
            return False
    return True


def _needlink(source, target):
    return os.path.exists(source) and not os.path.islink(target)


def _readlinesfromfile(path):
    if not os.path.exists(path):
        tools.runshell('touch %s' % path)
    with open(path, 'r') as f:
        lines = f.readlines()
    return lines


def new(formula):
    formulapath = _get_formulapath(formula)
    if not os.path.exists(formulapath):
        formuladic = {}
        formuladic['description'] = formula
        formuladic['check'] = []
        formuladic['install'] = []
        formuladic['uninstall'] = []
        formuladic['link'] = []
        tools.yamldump(formuladic, formulapath)
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
    """TODO: Docstring for list.
    :returns: TODO

    """
    msg = ''
    for formula in os.listdir(_path('core.formulalib')):
        name = _getformulaname(formula)
        if name:
            msg += '%s\t' % name
    if msg:
        _echo(msg)


def edit(formula):
    new(formula)


def info(formula):
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
            if not _checkinstall(formuladic):
                return
            configlib = tools.absolutepath(_getitem('core.configlib'))
            workpath = os.path.join(configlib, formula)
            links = formuladic.get('link', {})
            for target, source in links.items():
                target = tools.absolutepath(target)
                if source.startswith('.'):
                    source = os.path.join(workpath, os.path.basename(source))
                if _needlink(source, target):
                    if os.path.exists(target):
                        backuppath = os.path.join(ENVSLIB, 'backup')
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
            if not _checkinstall(formuladic):
                return
            links = formuladic.get('link', {})
            for target, _ in links.items():
                target = tools.absolutepath(target)
                if os.path.islink(target):
                    os.remove(target)


def zsh(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if not formuladic:
                return
            if not _checkinstall(formuladic):
                return
            zshconfigs = formuladic.get('zsh', [])
            zshconfigs = list(map(lambda n: n + '\n', zshconfigs))
            configlib = tools.absolutepath(_getitem('core.configlib'))
            workpath = os.path.join(configlib, formula)
            formulazshrc = os.path.join(workpath, '%s.zshrc' % formula)
            with open(formulazshrc, 'w') as f:
                f.writelines(zshconfigs)
            content = 'source %s\n' % formulazshrc
            envszshrc = os.path.join(ENVSLIB, 'envs.zshrc')
            if not os.path.exists(envszshrc):
                zshlist = []
            else:
                with open(envszshrc, 'r') as f:
                    zshlist = f.readlines()
            if content not in zshlist:
                zshlist.append(content)
                with open(envszshrc, 'w') as f:
                    f.writelines(zshlist)


def unzsh(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if not formuladic:
                return
            if not _checkinstall(formuladic):
                return
            configlib = tools.absolutepath(_getitem('core.configlib'))
            workpath = os.path.join(configlib, formula)
            formulazshrc = os.path.join(workpath, '%s.zshrc' % formula)
            envszshrc = os.path.join(ENVSLIB, 'envs.zshrc')
            if not os.path.exists(envszshrc):
                return
            with open(envszshrc, 'r') as f:
                zshrc = f.readlines()
            content = 'source %s\n' % formulazshrc
            try:
                zshrc.remove(content)
            except ValueError:
                return
            else:
                with open(envszshrc, 'w') as f:
                    f.writelines(zshrc)


def install(**kwargs):
    for formula in kwargs['formulas']:
        formulapath = _get_formulapath(formula)
        if not os.path.exists(formulapath):
            _echo('%s does not exist!' % formula)
        else:
            formuladic = _readformula(formulapath)
            if not formuladic:
                return
            if _checkinstall(formuladic):
                _echo('%s already installed' % formula)
            else:
                # run install cmds
                cmds = formuladic.get('install', [])
                tools.runshell(cmds)
                configlib = tools.absolutepath(_getitem('core.configlib'))
                os.makedirs(os.path.join(configlib, formula), exist_ok=True)
                # link config file
                link(formulas=[formula])
                # zsh
                zsh(formulas=[formula])
                # write to sync file
                if _checkinstall(formuladic):
                    with open(os.path.join(ENVSLIB, 'envs.local'), 'a') as f:
                        f.write('%s\n' % formula)
                    needsync = kwargs.get('sync', True)
                    if needsync:
                        with open(os.path.join(configlib, SYNCFILE), 'a') as f:
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
            if not _checkinstall(formuladic):
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
                if not _checkinstall(formuladic):
                    localpath = os.path.join(ENVSLIB, 'envs.local')
                    formulas_local = _readlinesfromfile(localpath)
                    formulas_local.remove('%s\n' % formula)
                    with open(localpath, 'w') as f:
                        f.writelines(formulas_local)
                    needsync = kwargs.get('sync', True)
                    if needsync:
                        configlib = tools.absolutepath(_getitem('core.configlib'))
                        syncpath = os.path.join(configlib, SYNCFILE)
                        formulas_sync = _readlinesfromfile(syncpath)
                        formula = formula + '\n'
                        if formula in formulas_sync:
                            formulas_sync.remove(formula)
                            with open(syncpath, 'w') as f:
                                f.writelines(formulas_sync)


def config(**kwargs):
    if kwargs['l']:
        tools.runshell('cat %s' % CONFIGPATH)
    else:
        tools.runshell('%s %s' % (EDITOR, CONFIGPATH))


def sync():
    # read syncfile
    configlib = tools.absolutepath(_getitem('core.configlib'))
    syncpath = os.path.join(configlib, SYNCFILE)
    formulas_sync = _readlinesfromfile(syncpath)
    localpath = os.path.join(ENVSLIB, 'envs.local')
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


def test():
    configlib = tools.absolutepath(_getitem('core.configlib'))
    _echo(configlib)
