#!/usr/bin/python

import argparse
import logging
from typing import List, Optional

from wickedjukebox import __version__
from wickedjukebox.logutil import setup_logging
from wickedjukebox.scanner import scan

LOG = logging.getLogger(__name__)


def process_rescan(args: argparse.Namespace) -> int:
    for path in args.path:
        scan(path)
    return 0


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parses the command-line arguments
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Subcommands help")
    rescan_parser = subparsers.add_parser("rescan")
    rescan_parser.add_argument("path", nargs=1)
    rescan_parser.set_defaults(func=process_rescan)
    return parser.parse_args(args)


def main() -> int:
    setup_logging(1)
    args = parse_args()
    return args.func(args)
