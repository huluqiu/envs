#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from . import commands


command_new = {
    'help': 'new formula',
    'arguments': [
        {'name': 'formula'}
    ]
}

command_delete = {
    'help': 'delete formula',
    'arguments': [
        {'name': 'formula'}
    ]
}

command_edit = {
    'help': 'edit formula',
    'arguments': [
        {'name': 'formula'}
    ]
}

command_info = {
    'help': 'show formula info',
    'arguments': [
        {'name': 'formula'}
    ]
}

command_list = {
    'help': 'list all formulas',
    'func': 'show_list',
    'arguments': []
}

command_install = {
    'help': 'install formula',
    'arguments': [
        {'name': 'formulas', 'nargs': '*'}
    ]
}

command_uninstall = {
    'help': 'uninstall formula',
    'arguments': [
        {'name': 'formulas', 'nargs': '*'}
    ]
}

command_link = {
    'help': 'link config file',
    'arguments': [
        {'name': 'formulas', 'nargs': '*'}
    ]
}

command_unlink = {
    'help': 'unlink config file',
    'arguments': [
        {'name': 'formulas', 'nargs': '*'}
    ]
}

command_sync = {
    'help': 'sync',
    'arguments': []
}

command_config = {
    'help': 'config',
    'arguments': [
        {'name': '-l', 'action': 'store_true', 'help': 'show config'},
    ]
}

command_test = {
    'help': 'test',
    'arguments': []
}

command_zsh = {
    'help': 'add config to .zshrc',
    'arguments': [
        {'name': 'formulas', 'nargs': '*'}
    ]
}

command_unzsh = {
    'help': 'remove config from .zshrc',
    'arguments': [
        {'name': 'formulas', 'nargs': '*'}
    ]
}

subparser_config = {
    'new': command_new,
    'delete': command_delete,
    'edit': command_edit,
    'info': command_info,
    'list': command_list,
    'install': command_install,
    'uninstall': command_uninstall,
    'link': command_link,
    'unlink': command_unlink,
    'zsh': command_zsh,
    'unzsh': command_unzsh,
    'sync': command_sync,
    'config': command_config,
    'test': command_test,
}


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')
    for cmd, config in subparser_config.items():
        subparser = subparsers.add_parser(cmd, help=config['help'])
        for argument in config['arguments']:
            argname = argument.pop('name')
            subparser.add_argument(argname, **argument)
    args = parser.parse_args()
    if args.subparser:
        func = subparser_config[args.subparser].get('func', args.subparser)
        fun = getattr(commands, func)
        args = vars(args)
        args.pop('subparser', None)
        fun(**args)


if __name__ == "__main__":
    main()
