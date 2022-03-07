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

from . import PluginTestCase

from naslinter.plugin import LinterError
from naslinter.plugins.prod_svc_detect_in_vulnvt import (
    CheckProdSvcDetectInVulnvt,
)


class CheckProdSVCDetectInVulnvtTestCase(PluginTestCase):
    def test_ok(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base", value:"0.0");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            'script_tag(name:"solution_type", value:"VendorFix");\n'
            'script_tag(name:"solution", value:"meh");\n'
        )

        results = list(
            CheckProdSvcDetectInVulnvt.run(
                nasl_file,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 0)

    def test_nok(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base", value:"4.0");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            'script_tag(name:"solution_type", value:"VendorFix");\n'
            'script_tag(name:"solution", value:"meh");\n'
            'script_family("Product detection");\n'
        )

        results = list(
            CheckProdSvcDetectInVulnvt.run(
                nasl_file,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            "VT has a severity but is placed in the family 'Product detection' "
            "which is not allowed for this VT. Please split this VT into a "
            "separate Product/Service detection and Vulnerability-VT.",
            results[0].message,
        )

    def test_nok2(self):
        nasl_file = Path(__file__).parent / "test.nasl"
        content = (
            'script_tag(name:"cvss_base", value:"4.0");\n'
            'script_tag(name:"summary", value:"Foo Bar.");\n'
            'script_tag(name:"solution_type", value:"VendorFix");\n'
            'script_tag(name:"solution", value:"meh");\n'
            'script_family("Product detection");\n'
            "register_product(cpe:cpe);\n"
        )

        results = list(
            CheckProdSvcDetectInVulnvt.run(
                nasl_file,
                content,
                tag_pattern=self.tag_pattern,
                special_tag_pattern=self.special_tag_pattern,
            )
        )
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], LinterError)
        self.assertEqual(
            "VT has a severity but is placed in the family 'Product detection' "
            "which is not allowed for this VT. Please split this VT into a "
            "separate Product/Service detection and Vulnerability-VT.",
            results[0].message,
        )
        self.assertEqual(
            "VT has a severity but is using the function 'register_product' "
            "which is not allowed for this VT. Please split this VT into a "
            "separate Product/Service detection and Vulnerability-VT.",
            results[1].message,
        )
