#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from . import commands


subparser_config = {
    'new': {
        'help': 'new formula',
        'arguments': ['formula'],
    },
    'delete': {
        'help': 'delete formula',
        'arguments': ['formula'],
    },
    'install': {
        'help': 'install formula',
        'arguments': ['formula'],
    },
    'uninstall': {
        'help': 'uninstall formula',
        'arguments': ['formula'],
    },
    'sync': {
        'help': 'sync',
        'arguments': [],
    },
    'edit': {
        'help': 'edit formula',
        'arguments': ['formula'],
    },
    'list': {
        'help': 'list all formulas',
        'func': 'show_list',
        'arguments': [],
    },
    'info': {
        'help': 'show formula info',
        'arguments': ['formula'],
    },
    'config': {
        'help': 'config',
        'arguments': ['item', 'value'],
    }
}


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')
    subparsers.parsers = {}
    for key, value in subparser_config.items():
        parser_key = subparsers.add_parser(key, help=value['help'])
        for argument in value['arguments']:
            parser_key.add_argument(argument)
        subparsers.parsers[key] = parser_key
    args = parser.parse_args()

    if args.subparser:
        func = subparser_config.get(args.subparser).get('func', args.subparser)
        fun = getattr(commands, func)
        args = vars(args)
        args.pop('subparser', None)
        fun(**args)


if __name__ == "__main__":
    main()
