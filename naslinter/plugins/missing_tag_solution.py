# Copyright (C) 2022 Greenbone Networks GmbH
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

from pathlib import Path
from typing import Iterator

from naslinter.helper import is_ignore_file

from naslinter.plugin import LinterError, FileContentPlugin, LinterResult
from naslinter.helper.patterns import get_tag_pattern, ScriptTag

# We don't want to touch the metadata of this older VTs...
_IGNORE_FILES = [
    "nmap_nse/",
]


class CheckMissingTagSolution(FileContentPlugin):
    name = "check_missing_tag_solution"

    @staticmethod
    def run(nasl_file: Path, file_content: str) -> Iterator[LinterResult]:
        """This script checks if the VT has a solution_type script tag:
        script_tag(name:"solution_type", value:"");

        but is missing a solution tag within the description block like:
        script_tag(name:"solution", value:"");

        This excludes files from the (sub)dir "nmap_nse/" and deprecated
        vts.
        """
        if is_ignore_file(nasl_file, _IGNORE_FILES):
            return
        # Not all VTs have/require a solution_type text
        if "solution_type" not in file_content:
            return
        # Avoid unnecessary message against deprecated VTs.
        deprecated_match = get_tag_pattern(
            name=ScriptTag.DEPRECATED, value="TRUE"
        ).search(string=file_content)

        if deprecated_match and deprecated_match.group("value"):
            return

        solution_type_match = get_tag_pattern(
            name=ScriptTag.SOLUTION_TYPE
        ).search(string=file_content)
        if not solution_type_match and solution_type_match.group(0):
            return

        solution_match = get_tag_pattern(
            name=ScriptTag.SOLUTION, flags=re.MULTILINE | re.DOTALL
        ).search(string=file_content)

        if not solution_match or solution_match.group(0) is None:
            yield LinterError(
                "'solution_type' script_tag but no 'solution' script_tag "
                "found in the description block."
            )
