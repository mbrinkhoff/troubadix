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

import re
from collections import Counter
from typing import Iterator

from troubadix.helper.patterns import _get_special_script_tag_pattern
from troubadix.plugin import FilePlugin, LinterError, LinterResult


class CheckMalformedDependencies(FilePlugin):
    name = "check_malformed_dependencies"

    def run(
        self,
    ) -> Iterator[LinterResult]:
        """This script checks whether the files used in script_dependencies()
        exist on the local filesystem.
        An error will be thrown if a dependency could not be found.
        """

        if self.context.nasl_file.suffix == ".inc":
            return

        dependencies_pattern = _get_special_script_tag_pattern(
            "dependencies", flags=re.DOTALL | re.MULTILINE
        )

        file_content = self.context.file_content

        matches = dependencies_pattern.finditer(file_content)

        for match in matches:
            if not match:
                continue

            counter = Counter(
                f'"{match.group("value")}"' if match.group("value") else ""
            )
            quote_count = counter.get('"', 0) + counter.get("'", 0)
            comma_count = counter.get(",", 0)

            required_comma_count = quote_count / 2 - 1
            if quote_count >= 2 and comma_count != required_comma_count:
                yield LinterError(
                    "The script dependency value is malformed and "
                    "contains an invalid ratio of quoted entries to commas",
                    file=self.context.nasl_file,
                    plugin=self.name,
                )
