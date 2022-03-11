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
from typing import Iterator, OrderedDict
from naslinter.helper.patterns import get_xref_pattern

from naslinter.plugin import FileContentPlugin, LinterError, LinterResult


class CheckScriptXrefForm(FileContentPlugin):
    name = "check_script_xref_form"

    @staticmethod
    def run(
        nasl_file: Path,
        file_content: str,
        *,
        tag_pattern: OrderedDict[str, re.Pattern],
        special_tag_pattern: OrderedDict[str, re.Pattern],
    ) -> Iterator[LinterResult]:
        """
        Checks for correct parameters for script_xref calls
        """
        del tag_pattern, special_tag_pattern
        if nasl_file.suffix == ".inc":
            return

        matches = re.finditer(r"script_xref\(.*\);", file_content)
        if matches:
            for match in matches:
                if match:
                    if not get_xref_pattern(name=".*", value=".*").match(
                        match.group(0)
                    ):
                        yield LinterError(
                            f"{match.group(0)}: does not conform to"
                            ' script_xref(name:"<name>", value:<value>);'
                        )
