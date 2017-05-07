#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from . import commands


subparser_config = {
    'new': {
        'help': 'new poke',
        'arguments': ['poke'],
    },
    'delete': {
        'help': 'delete poke',
        'arguments': ['poke'],
    },
    'install': {
        'help': 'install poke',
        'arguments': ['poke'],
    },
    'uninstall': {
        'help': 'uninstall poke',
        'arguments': ['poke'],
    },
    'sync': {
        'help': 'sync',
        'arguments': [],
    },
    'edit': {
        'help': 'edit poke',
        'arguments': ['poke'],
    },
    'list': {
        'help': 'list all pokes',
        'arguments': [],
    },
    'info': {
        'help': 'show poke info',
        'arguments': ['poke'],
    },
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
        fun = getattr(commands, args.subparser)
        if 'poke' in dir(args):
            fun(args.poke)
        else:
            fun()


if __name__ == "__main__":
    main()
