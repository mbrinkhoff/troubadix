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
from naslinter.helper.patterns import get_special_tag_pattern, get_tag_pattern

from naslinter.plugin import FileContentPlugin, LinterResult, LinterWarning


class CheckScriptCallsRecommended(FileContentPlugin):
    name = "check_script_calls_recommended"

    @staticmethod
    def run(
        nasl_file: Path,
        file_content: str,
        *,
        tag_pattern: OrderedDict[str, re.Pattern],
        special_tag_pattern: OrderedDict[str, re.Pattern],
    ) -> Iterator[LinterResult]:
        """
        This script checks for the existence of recommended script calls. These
        are categorize int two groups. In group 2 it is recommended to call
        every single one. In group 1 it is sufficient to call one of the script
        calls.

        group1:
        - script_dependencies

        group2:
        - script_require_ports
        - script_require_udp_ports
        - script_require_keys
        - script_mandatory_keys
        """
        del tag_pattern, special_tag_pattern
        if nasl_file.suffix == ".inc":
            return

        if get_special_tag_pattern(
            name=r"category", value=r"ACT_(SETTINGS|SCANNER|INIT)"
        ).search(file_content) or get_tag_pattern(
            name=r"deprecated", value=r"TRUE"
        ).search(
            file_content
        ):
            return

        recommended_single_call = [r"dependencies"]
        recommended_many_call = [
            r"required_ports",
            r"require_udp_ports",
            r"require_keys",
            r"mandatory_keys",
        ]

        if not get_special_tag_pattern(
            name=rf"({'|'.join(recommended_many_call)})", value=".*"
        ).search(file_content):
            yield LinterWarning(
                "VT contains none of the following recommended calls: "
                f"{', '.join(recommended_many_call)}"
            )
        for call in recommended_single_call:
            if not get_special_tag_pattern(name=call, value=".*").search(
                file_content
            ):
                yield LinterWarning(
                    "VT does not contain the following recommended call: "
                    f"'script_{call}'"
                )
