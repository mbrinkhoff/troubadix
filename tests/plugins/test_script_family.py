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
from naslinter.plugins.script_family import CheckScriptFamily

from . import PluginTestCase


class CheckNewlinesTestCase(PluginTestCase):
    def test_ok(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base_vector", value:"AV:N/A:N");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            "script_bugtraq_id(00000);\n"
            'script_family("FreeBSD Local Security Checks");\n'
        )

        results = list(
            CheckScriptFamily.run(
                nasl_file,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 0)

    def test_script_family(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base_vector", value:"AV:N/A:N");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            "script_bugtraq_id(00000);\n"
            'script_family("TestTest");\n'
        )

        results = list(
            CheckScriptFamily.run(
                nasl_file,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            'Invalid or misspelled script family "TestTest"', results[0].message
        )

    def test_script_family2(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base_vector", value:"AV:N/A:N");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            "script_bugtraq_id(00000);\n"
        )

        results = list(
            CheckScriptFamily.run(
                nasl_file,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual("No script family exist", results[0].message)

    def test_script_family3(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base_vector", value:"AV:N/A:N");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            'script_family("???\\");\n'
            'script_family("???\\");\n'
            "script_bugtraq_id(00000);\n"
        )

        results = list(
            CheckScriptFamily.run(
                nasl_file,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            "More then one script family exist", results[0].message
        )
