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

# pylint: disable=fixme

from enum import Enum

from pathlib import Path
import re
from typing import Iterator, OrderedDict
from naslinter.helper.patterns import SpecialScriptTag, get_special_tag_pattern

from naslinter.plugin import (
    LinterError,
    FileContentPlugin,
    LinterResult,
)


class ValidType(Enum):
    CHECKBOX = "checkbox"
    PASSWORD = "password"
    FILE = "file"
    RADIO = "radio"
    ENTRY = "entry"


class CheckScriptAddPreferenceType(FileContentPlugin):
    name = "check_script_add_preference_type"

    @staticmethod
    def run(
        nasl_file: Path,
        file_content: str,
        *,
        tag_pattern: OrderedDict[str, re.Pattern],
        special_tag_pattern: OrderedDict[str, re.Pattern],
    ) -> Iterator[LinterResult]:
        """This script checks the passed VT if it is using a
        script_add_preference not matching one of the following
        allowed strings passed to the 'type' function parameter:

            - checkbox
            - password
            - file
            - radio
            - entry

        Args:
            file: The VT that is going to be checked
        """
        # don't need to check VTs not having a script_add_preference() call
        if "script_add_preference" not in file_content:
            return

        preferences_matches = get_special_tag_pattern(
            name=SpecialScriptTag.ADD_PREFERENCE,
            value=r'type\s*:\s*[\'"](?P<type>[^\'"]+)[\'"]\s*[^)]*',
        ).finditer(file_content)

        for preferences_match in preferences_matches:
            if preferences_match:

                pref_type = preferences_match.group("type")
                if pref_type not in [t.value for t in ValidType]:

                    # nb: This exists since years and it is currently
                    # unclear if we can change it so
                    # we're excluding it here for now.
                    if (
                        "ssh_authorization_init.nasl" in nasl_file.name
                        and pref_type == "sshlogin"
                    ):
                        continue

                    yield LinterError(
                        "VT is using an invalid or misspelled string "
                        f"({pref_type}) passed to the type parameter of "
                        "script_add_preference in "
                        f"'{preferences_match.group(0)}'"
                    )
