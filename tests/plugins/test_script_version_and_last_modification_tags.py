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
from pathlib import Path

import unittest

from naslinter.plugin import LinterError
from naslinter.plugins.script_version_and_last_modification_tags import (
    CheckScriptVersionAndLastModificationTags,
)


class CheckScriptVersionAndLastModificationTagsTestCase(unittest.TestCase):
    def test_ok(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base", value:"4.0");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            'script_tag(name:"solution_type", value:"VendorFix");\n'
            'script_tag(name:"solution", value:"meh");\n'
            'script_version("2021-07-19T12:32:02+0000");\n'
            'script_tag(name: "last_modification", value: "2021-07-19 '
            '12:32:02 +0000 (Mon, 19 Jul 2021)");\n'
        )

        results = list(
            CheckScriptVersionAndLastModificationTags.run(nasl_file, content)
        )
        print(results)
        self.assertEqual(len(results), 0)

    def test_nok(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base", value:"4.0");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            'script_tag(name:"solution_type", value:"VendorFix");\n'
            'script_tag(name:"solution", value:"meh");\n'
        )

        results = list(
            CheckScriptVersionAndLastModificationTags.run(nasl_file, content)
        )
        print(results)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            f"VT '{str(nasl_file)}' is missing script_version(); or is using "
            "a wrong syntax.\n",
            results[0].message,
        )
        self.assertEqual(
            f"VT '{str(nasl_file)}' is missing script_tag("
            f'name:"last_modification" or is using a wrong syntax.\n',
            results[1].message,
        )
