#  Copyright (c) 2022 Greenbone Networks GmbH
#
#  SPDX-License-Identifier: GPL-3.0-or-later
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import re

from pathlib import Path
from typing import Iterator

from naslinter.plugin import LinterError, FileContentPlugin, LinterResult


class CheckWrongSetGetKBCalls(FileContentPlugin):
    name = "check_set_get_kb_calls"

    @staticmethod
    def run(nasl_file: Path, file_content: str) -> Iterator[LinterResult]:
        """
        Checks a given file if it calls any of the following functions setting
        or getting KB entries in a wrong way like e.g. with too much or too
        less function parameters.

        - set_kb_item(name:"kb/key", value:"value");
        - replace_kb_item(name:"kb/key", value:"value");
        - get_kb_item("kb/key");
        - get_kb_list("kb/key");

        Wrong examples which needs to be reported:

        - set_kb_item("kb/key", value:"value");
        - replace_kb_item(name:"kb/key", "value");
        - replace_kb_item(name:"kb/key");
        - replace_kb_item(name:"kb/key", name:"kb/key");
        - get_kb_item(name:"kb/key");

        Args:
            nasl_file: The VT/Include that is going to be checked
            file_content: The content of the nasl_file

        """

        found_wrong_set_calls = ""
        found_wrong_get_calls = ""
        param_re = re.compile(r"(name|value) ?:")

        set_matches = re.finditer(
            r"(set|replace)_kb_item\s*\(([^)]+)\)\s*;",
            file_content,
            re.MULTILINE,
        )
        if set_matches is not None:
            for set_match in set_matches:
                if set_match is not None and set_match.group(2) is not None:
                    set_param_match = re.findall(param_re, set_match.group(2))
                    if not set_param_match or len(set_param_match) != 2:
                        found_wrong_set_calls += "\n\t" + set_match.group(0)

        get_matches = re.finditer(
            r"get_kb_(item|list)\s*\(([^)]+)\)\s*;", file_content, re.MULTILINE
        )
        if get_matches is not None:
            for get_match in get_matches:
                if get_match is not None and get_match.group(2) is not None:
                    get_param_match = re.findall(param_re, get_match.group(2))
                    if get_param_match and len(get_param_match) > 0:
                        found_wrong_get_calls += "\n\t" + get_match.group(0)

        if len(found_wrong_set_calls) > 0:
            yield LinterError(
                "The VT/Include are missing a 'name:' and/or "
                f"'value:' parameter:{found_wrong_set_calls}"
            )

        if len(found_wrong_get_calls) > 0:
            if len(found_wrong_set_calls) > 0:
                yield LinterError(
                    "The VT/Include are using a non-existent 'name:' "
                    f"and/or 'value:' parameter:{found_wrong_get_calls}"
                )
