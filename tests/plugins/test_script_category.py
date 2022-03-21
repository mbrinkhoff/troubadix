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

from troubadix.plugin import LinterError
from troubadix.plugins.script_category import CheckScriptCategory

from . import PluginTestCase


class CheckScriptCategoryTestCase(PluginTestCase):
    def test_ok(self):
        path = Path("some/file.nasl")
        content = "script_category(ACT_GATHER_INFO);"

        results = list(
            CheckScriptCategory.run(
                path,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 0)

    def test_missing_category(self):
        path = Path("some/file.nasl")
        content = ""

        results = list(
            CheckScriptCategory.run(
                path,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            "VT is missing a script_category.",
            results[0].message,
        )

    def test_invalid_category(self):
        path = Path("some/file.nasl")
        content = "script_category(ACT_FOO);"

        results = list(
            CheckScriptCategory.run(
                path,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            "VT is using an unsupported category 'ACT_FOO'.",
            results[0].message,
        )
