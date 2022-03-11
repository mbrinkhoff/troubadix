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

from naslinter.plugin import LinterError
from naslinter.plugins.script_tag_form import CheckScriptTagForm
from tests.plugins import PluginTestCase


class CheckScriptTagFormTestCase(PluginTestCase):
    path = Path("some/file.nasl")

    def test_ok(self):

        content = (
            'script_tag(name: "foo", value:"bar");\n'
            'script_tag(name: "foo", value:42);'
        )

        results = list(
            CheckScriptTagForm.run(
                nasl_file=self.path,
                file_content=content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 0)

    def test_wrong_name(self):
        content = 'script_tag(nammmme: "foo", value:"bar");'

        results = list(
            CheckScriptTagForm.run(
                nasl_file=self.path,
                file_content=content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            'script_tag(nammmme: "foo", value:"bar");: does not conform to'
            ' script_tag(name:"<name>", value:<value>);',
            results[0].message,
        )

    def test_wrong_value(self):
        content = 'script_tag(name: "foo", valueeeee:"bar");'

        results = list(
            CheckScriptTagForm.run(
                nasl_file=self.path,
                file_content=content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)

    def test_wrong_missing_parameters(self):
        content = 'script_tag("foo", "bar");'

        results = list(
            CheckScriptTagForm.run(
                nasl_file=self.path,
                file_content=content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
