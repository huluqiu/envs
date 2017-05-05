#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import commands


subparser_config = {
    'new': {
        'help': 'new package',
        'arguments': ['package'],
    },
    'delete': {
        'help': 'delete package',
        'arguments': ['package'],
    },
    'install': {
        'help': 'install package',
        'arguments': ['package'],
    },
    'uninstall': {
        'help': 'uninstall package',
        'arguments': ['package'],
    },
    'sync': {
        'help': 'sync',
        'arguments': [],
    },
    'edit': {
        'help': 'edit package',
        'arguments': ['package'],
    },
    'list': {
        'help': 'list all packages',
        'arguments': [],
    },
    'info': {
        'help': 'show package info',
        'arguments': ['package'],
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

    fun = getattr(commands, args.subparser)
    if 'package' in dir(args):
        fun(args.package)
    else:
        fun()


if __name__ == "__main__":
    main()
