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

from enum import IntEnum
import re

from pathlib import Path
from typing import Iterator, Union

from naslinter.plugin import (
    LinterError,
    FileContentPlugin,
    LinterResult,
)
from naslinter.helper import get_root, get_special_tag_pattern, SpecialScriptTag

# See https://shorturl.at/jBGJT for a list of the category numbers.
class VTCategory(IntEnum):
    ACT_INIT = 0
    ACT_SCANNER = 1
    ACT_SETTINGS = 2
    ACT_GATHER_INFO = 3
    ACT_ATTACK = 4
    ACT_MIXED_ATTACK = 5
    ACT_DESTRUCTIVE_ATTACK = 6
    ACT_DENIAL = 7
    ACT_KILL_HOST = 8
    ACT_FLOOD = 9
    ACT_END = 10


def check_category(
    content: str, script: str = ""
) -> Union[LinterError, VTCategory]:
    """Check if the content contains a script category
    Arguments:
        content         the content to check

    Returns:
        LinterError     if no category found or category invalid
        VTCategory      else
    """
    match = get_special_tag_pattern(name=SpecialScriptTag.CATEGORY).search(
        content
    )

    if not match:
        return LinterError(f"{script}: Script category is missing.")

    category_value = match.group("value")
    if category_value not in dir(VTCategory):
        return LinterError(
            f"{script}: Script category {category_value} is unsupported."
        )

    return VTCategory[category_value]


class CheckDependencyCategoryOrder(FileContentPlugin):
    name = "check_dependency_category_order"

    @staticmethod
    def run(nasl_file: Path, file_content: str) -> Iterator[LinterResult]:
        """No VT N should depend on scripts that are in a category that
        normally would be executed after the category of VT M.
        e.g. a VT N within the ACT_GATHER_INFO category (3) is
        not allowed to depend on a VT M within the ACT_ATTACK category (4).
        See https://shorturl.at/jBGJT for a list of such category numbers.

        In addition it is not allowed for VTs to have a direct dependency
        to VTs from within the ACT_SCANNER category.
        """
        if not "script_dependencies(" in file_content:
            return

        root = get_root(nasl_file)

        category = check_category(content=file_content, script=nasl_file.name)
        if isinstance(category, LinterError):
            yield category
            return

        matches = get_special_tag_pattern(
            name=SpecialScriptTag.DEPENDENCIES
        ).finditer(file_content)

        if not matches:
            return
        for match in matches:
            if match:
                # Remove single and/or double quotes, spaces
                # and create a list by using the comma as a separator
                dependencies = re.sub(
                    r'[\'"\s]', "", match.group("value")
                ).split(",")

                for dep in dependencies:
                    dependency_path = Path(root / dep)
                    if not dependency_path.exists():
                        yield LinterError(
                            f"The script dependency {dep} could not "
                            "be found within the VTs."
                        )
                    else:
                        # TODO: gsf/PCIDSS/PCI-DSS.nasl,
                        # gsf/PCIDSS/v2.0/PCI-DSS-2.0.nasl
                        # and GSHB/EL15/GSHB.nasl
                        # are using a variable which we currently can't handle.
                        if "+d+.nasl" in dep:
                            continue

                        dependency_content = dependency_path.read_text(
                            encoding="latin1"
                        )

                        dependency_category = check_category(
                            content=dependency_content,
                            script=dependency_path.name,
                        )
                        if isinstance(dependency_category, LinterError):
                            yield dependency_category

                        if category.value < dependency_category.value:
                            yield LinterError(
                                f"Script category {category.name}"
                                f"({category.value}) is lower than "
                                f"the category {dependency_category.name}"
                                f"({dependency_category.value}) of the "
                                f"dependency {dep}."
                            )
                        # nb: Currently not sure about the
                        # host_alive_detection.nasl dependency so
                        # excluding them for now.
                        if (
                            dependency_category.name == "ACT_SCANNER"
                            and dep != "host_alive_detection.nasl"
                        ):
                            yield LinterError(
                                f"Script depends on {dep} which has the "
                                f"category {dependency_category.name}"
                                f"({dependency_category.value}), but no VT"
                                " is allowed to have a direct dependency "
                                "to VTs in this category."
                            )
