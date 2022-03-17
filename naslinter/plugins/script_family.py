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

import re
from pathlib import Path
from typing import Iterator, OrderedDict

from naslinter.plugin import FileContentPlugin, LinterResult, LinterError

VALID_FAMILIES = [
    "AIX Local Security Checks",
    "Amazon Linux Local Security Checks",
    "Brute force attacks",
    "Buffer overflow",
    "CISCO",
    "CentOS Local Security Checks",
    "Citrix Xenserver Local Security Checks",
    "Compliance",
    "Credentials",
    "Databases",
    "Debian Local Security Checks",
    "Default Accounts",
    "Denial of Service",
    "F5 Local Security Checks",
    "FTP",
    "Fedora Local Security Checks",
    "FortiOS Local Security Checks",
    "FreeBSD Local Security Checks",
    "Gain a shell remotely",
    "General",
    "Gentoo Local Security Checks",
    "Huawei",
    "Huawei EulerOS Local Security Checks",
    "HP-UX Local Security Checks",
    "IT-Grundschutz",
    "IT-Grundschutz-deprecated",
    "IT-Grundschutz-15",
    "JunOS Local Security Checks",
    "Mac OS X Local Security Checks",
    "Mageia Linux Local Security Checks",
    "Malware",
    "Mandrake Local Security Checks",
    "Nmap NSE",
    "Nmap NSE net",
    "Oracle Linux Local Security Checks",
    "PCI-DSS",
    "PCI-DSS 2.0",
    "Palo Alto PAN-OS Local Security Checks",
    "Peer-To-Peer File Sharing",
    "Policy",
    "Port scanners",
    "Privilege escalation",
    "Product detection",
    "RPC",
    "Red Hat Local Security Checks",
    "Remote file access",
    "SMTP problems",
    "SNMP",
    "SSL and TLS",
    "Service detection",
    "Settings",
    "Slackware Local Security Checks",
    "Solaris Local Security Checks",
    "SuSE Local Security Checks",
    "Ubuntu Local Security Checks",
    "Useless services",
    "VMware Local Security Checks",
    "Web Servers",
    "Web application abuses",
    "Windows",
    "Windows : Microsoft Bulletins",
]


class CheckScriptFamily(FileContentPlugin):
    name = "check_script_family"

    @staticmethod
    def run(
        nasl_file: Path,
        file_content: str,
        *,
        tag_pattern: OrderedDict[str, re.Pattern],
        special_tag_pattern: OrderedDict[str, re.Pattern],
    ) -> Iterator[LinterResult]:
        """This script checks VT for the existence / validity
        of its script family"""
        del tag_pattern, special_tag_pattern

        if nasl_file.suffix == ".inc":
            return

        match = re.findall(
            r'script_family\s*\(["\']?(?P<script_family>.+?)["\']?\s*\)\s*;',
            file_content,
        )

        if not len(match):
            yield LinterError("No script family exist")
            return

        if len(match) > 1:
            yield LinterError("More then one script family exist")
            return

        if match[0] not in VALID_FAMILIES:
            yield LinterError(
                "Invalid or misspelled script family " f'"{match[0]}"'
            )
