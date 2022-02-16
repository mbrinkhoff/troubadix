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

import re

from typing import Iterable
from pathlib import Path

from ..plugin import LineContentPlugin, LinterError
from ..helper import is_ignore_file

_IGNORE_FILES = [
    "gb_openvas",
    "gb_gsa_",
    "http_func.inc",
    "misc_func.inc",
]


class CheckTodoTbd(LineContentPlugin):
    """This step checks if a given VT contains the words TODO, TBD
    or @todo as a comment.
    """

    name = "check_todo_tbd"

    @staticmethod
    def run(nasl_file: Path, lines: Iterable[str]):
        if is_ignore_file(nasl_file, _IGNORE_FILES):
            return
        for index, line in enumerate(lines, start=1):
            match = re.search("##? *(TODO|TBD|@todo):?", line)
            if match is not None:
                yield LinterError(
                    f"VT {nasl_file} contains #TODO/TBD/@todo"
                    f" keywords at line {index}"
                )
