# Copyright (C) 2021 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Argument parser for naslinter """

from argparse import ArgumentParser, Namespace
from pathlib import Path
import os

import sys
from typing import List


from pontos.terminal.terminal import Terminal


def directory_type(string: str) -> Path:
    directory_path = Path(string)
    if not directory_path.is_dir():
        raise ValueError(f"{string} is not a directory.")
    return directory_path


def file_type(string: str) -> Path:
    file_path = Path(string)
    if not file_path.is_file():
        raise ValueError(f"{string} is not a file.")
    return file_path


def parse_args(
    term: Terminal,
    *,
    args: List[str] = None,
) -> Namespace:
    """Parsing args for nasl-lint

    Arguments:
    args        The programm arguments passed by exec
    term        The terminal to print"""

    parser = ArgumentParser(
        description="Greenbone NASL File Linter.",
    )

    parser.add_argument(
        "-f",
        "--full",
        action="store_true",
        help=(
            "Checking the complete VT directory and "
            "not only the added/changed scripts"
        ),
    )

    what_group = parser.add_mutually_exclusive_group(required=False)

    what_group.add_argument(
        "-d",
        "--dirs",
        nargs="+",
        type=directory_type,
        help="List of directories that should be linted",
    )

    what_group.add_argument(
        "--files",
        nargs="+",
        type=file_type,
        help="List of files that should be linted",
    )

    what_group.add_argument(
        "--commit-range",
        nargs="+",
        type=str,
        help=(
            "Allows to specify a git commit range "
            '(e.g. "$commit-hash1 $commit-hash2" or '
            '"HEAD~1") to run the QA test against.'
        ),
    )

    what_group.add_argument(
        "--staged-only",
        action="store_true",
        help=('Only run against files which are "staged/added" in git'),
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help=("Enables the DEBUG output"),
    )

    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help=(
            "Don't run the script recursive. "
            'Only usable with "-f"/"--full" or "-d"/"--dirs"'
        ),
    )

    parser.add_argument(
        "--include-regex",
        type=str,
        nargs="+",
        help=(
            "Allows to specify a regex (glob) to "
            'limit the "--full"/"--dirs" run to specific file names. '
            'e.g. "gb_*.nasl", or "*some_vt*.nasl" or "some_dir/gb_*nasl". '
            'Only usable with "-f"/"--full" or "-d"/"--dirs".'
        ),
    )

    parser.add_argument(
        "--exclude-regex",
        type=str,
        nargs="+",
        help=(
            "Allows to specify a regex (glob) to "
            'exclude specific file names from the "--full"/"--dirs" run. '
            'e.g. "some_dir/*.nasl", "gb_*nasl", "*/anything.*'
            'Only usable with "-f"/"--full" or "-d"/"--dirs".'
        ),
    )

    tests_group = parser.add_mutually_exclusive_group(required=False)

    tests_group.add_argument(
        "--include-tests",
        type=str,
        nargs="+",
        dest="included_plugins",
        help=(
            "Allows to choose which tests should be run in this lint. "
            "Only the given tests will run."
        ),
    )

    tests_group.add_argument(
        "--exclude-tests",
        type=str,
        nargs="+",
        dest="excluded_plugins",
        help=(
            "Allows to exclude tests from this lint. "
            "All tests excluding the given will run."
        ),
    )

    parser.add_argument(
        "--skip-duplicated-oids",
        action="store_true",
        help=" Disables the check for duplicated OIDs in VTs",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stdout)
        sys.exit(1)

    parsed_args = parser.parse_args(args=args)

    # Full will run in the root directory of executing. (Like pwd)
    if parsed_args.full:
        cwd = Path(os.getcwd())
        term.info(f"Running full lint from {cwd}")
        parsed_args.dirs = [Path(cwd)]

    if not parsed_args.dirs and (
        parsed_args.include_regex or parsed_args.exclude_regex
    ):
        term.warning(
            "The arguments '--include-regex' and '--exclude-regex' "
            "must be used with '-f/--full' or '-d'/'--dirs'"
        )
        sys.exit(1)

    if not parsed_args.dirs and parsed_args.non_recursive:
        term.warning(
            "'Argument '--non-recursive' is only usable with "
            "'-f'/'--full' or '-d'/'--dirs'"
        )
        sys.exit(1)

    return parsed_args
