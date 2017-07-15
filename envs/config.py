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
