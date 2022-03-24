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

from pathlib import Path
from typing import Iterator

from troubadix.helper.patterns import (
    get_script_tag_patterns,
    get_special_script_tag_patterns,
)
from troubadix.plugin import FileContentPlugin, LinterError, LinterResult


class CheckDuplicatedScriptTags(FileContentPlugin):
    name = "check_duplicated_script_tags"

    @staticmethod
    def run(
        nasl_file: Path,
        file_content: str,
    ) -> Iterator[LinterResult]:
        special_script_tag_patterns = get_special_script_tag_patterns()
        for tag, pattern in special_script_tag_patterns.items():
            # TBD: script_name might also look like this:
            # script_name("MyVT (Windows)");
            match = pattern.finditer(file_content)

            if match:
                # This is allowed, see e.g.
                # gb_netapp_data_ontap_consolidation.nasl
                if tag.value == "dependencies" and "FEED_NAME" in file_content:
                    continue
                if tag.value == "xref":
                    continue
                match = list(match)
                if len(match) > 1:
                    yield LinterError(
                        f"The VT is using the script tag 'script_"
                        f"{tag.value}' multiple number of times."
                    )

        script_tag_patterns = get_script_tag_patterns()
        for tag, pattern in script_tag_patterns.items():
            match = pattern.finditer(file_content)

            if match:
                match = list(match)
                if len(match) > 1:
                    yield LinterError(
                        f"The VT is using the script tag '{tag.value}' "
                        "multiple number of times."
                    )
