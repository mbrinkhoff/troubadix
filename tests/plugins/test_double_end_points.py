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

import unittest

from naslinter.plugin import LinterError
from naslinter.plugins.double_end_points import CheckDoubleEndPoints


class CheckDoubleEndPointsTestCase(unittest.TestCase):
    def test_ok(self):
        path = Path("some/file.nasl")
        content = (
            'script_tag(name:"cvss_base", value:"4.0");\n'
            'script_tag(name:"summary", value:"Foo Bar.");'
        )

        results = list(CheckDoubleEndPoints.run(path, content))
        self.assertEqual(len(results), 0)

    def test_invalid(self):
        path = Path("some/file.nasl")
        content = (
            'script_tag(name:"cvss_base", value:"4.0");\n'
            'script_tag(name:"summary", value:"Foo Bar...");'
        )

        results = list(CheckDoubleEndPoints.run(path, content))
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            "The script tag 'summary' "
            "is ending with two or more points: "
            "'Foo Bar...'.",
            results[0].message,
        )
