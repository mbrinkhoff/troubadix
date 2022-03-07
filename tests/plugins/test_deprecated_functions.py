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

from . import PluginTestCase

from naslinter.plugin import LinterError
from naslinter.plugins.deprecated_functions import (
    CheckDeprecatedFunctions,
)


class CheckDeprecatedDependencyTestCase(PluginTestCase):
    def test_ok(self):
        path = Path("some/file.nasl")
        content = (
            'script_tag(name:"cvss_base", value:"4.0");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            "script_category(ACT_ATTACK);"
        )

        results = list(
            CheckDeprecatedFunctions.run(
                path,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 0)

    def test_deprecated_functions(self):
        deprecated_output = {
            'script_summary(), use script_tag(name:"'
            'summary", value:"") instead': "script_"
            "summary('this is not okay!');\n",
            "script_id(), use script_oid() with "
            "the full OID instead": "script_id(123345);\n",
            "security_note()": "security_note('nonono!');\n",
            "security_warning()": "security_warning('nonono!');\n",
            "security_hole()": "security_hole('nonono!');",
            "script_description()": "script_description('stop it!')\n",
            'script_tag(name:"risk_factor", value: '
            "SEVERITY)": 'script_tag(name:"risk_factor", value: 0.1);\n',
        }
        path = Path("some/file.nasl")
        for msg, cont in deprecated_output.items():
            content = (
                'script_tag(name:"cvss_base", value:"4.0");\n'
                'script_tag(name:"summary", value:"Foo Bar.");\n'
                f"script_category(ACT_ATTACK);\n{cont}"
            )

            results = list(
                CheckDeprecatedFunctions.run(
                    path,
                    content,
                    tag_pattern=self.tag_pattern,
                    special_tag_pattern=self.special_tag_pattern,
                )
            )

            self.assertEqual(len(results), 1)
            self.assertIsInstance(results[0], LinterError)
            self.assertEqual(
                f"Found a deprecated function call: {msg}",
                results[0].message,
            )
