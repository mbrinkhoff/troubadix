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

""" updating the modification time in VTs that have been touched/edited """

import datetime
from pathlib import Path
import re

from naslinter.plugin import LinterError, FileContentPlugin, LinterResult


class UpdateModificationDate(FileContentPlugin):
    name = "update_modification_date"

    @staticmethod
    def run(nasl_file: Path, file_content: str):

        tag_template = 'script_tag(name:"last_modification", value:"{date}");'

        pattern = r"script_tag\(name:\"last_modification\", value:\"(.*)\"\);"

        match = re.search(
            pattern=pattern,
            string=file_content,
        )
        if not match:
            yield LinterError(
                "File is not containing a modification day script tag."
            )

        old_datetime = match.groups()[0]

        now = datetime.datetime.now(datetime.timezone.utc)
        # get that stinky date formatted correctly
        correctly_formated_datetime = (
            f"{now:%Y-%m-%d %H:%M:%S %z (%a, %d %b %Y)}"
        )

        file_content = file_content.replace(
            f"{tag_template.format(date=old_datetime)}",
            f"{tag_template.format(date=correctly_formated_datetime)}",
        )

        nasl_file.write_text(file_content, encoding="latin1")

        yield LinterResult(
            f"Sucessfully replaced modification date {old_datetime} "
            f"with {correctly_formated_datetime}"
        )
