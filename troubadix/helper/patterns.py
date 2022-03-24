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

from enum import Enum
from typing import Dict

_XREF_TAG_PATTERN = (
    r'script_xref\(\s*name\s*:\s*["\'](?P<type>{type})["\']\s*,'
    r'\s*value\s*:\s*["\']?(?P<value>{value})["\']?\s*\)\s*;'
)


def get_xref_pattern(
    name: str,
    *,
    value: str = r".+",
    flags: re.RegexFlag = 0,
) -> re.Pattern:
    """
    The returned pattern catchs all `script_tags(name="", value="");`

    Arguments:
        name        script tag name
        value       script tag value (default: at least on char)
        flags       regex flags for compile (default: 0)

    The returned `Match`s by this pattern will have group strings
    .group('name') and .group('value')
    Returns
        `re.Pattern` object
    """
    return re.compile(
        _XREF_TAG_PATTERN.format(type=name, value=value),
        flags=flags,
    )


# regex patterns for script tags
_TAG_PATTERN = (
    r'script_tag\s*\(\s*name\s*:\s*["\'](?P<name>{name})["\']\s*,'
    r'\s*value\s*:\s*["\']?(?P<value>{value})["\']?\s*\)\s*;'
)


def _get_tag_pattern(
    name: str, *, value: str = r".+?", flags: re.RegexFlag = 0
) -> re.Pattern:
    """
    The returned pattern catches all `script_tags(name="", value="");`

    Arguments:
        name        a SpecialScriptTag Enum type
        value       script tag value (default: at least on char)
        flags       regex flags for compile (default: 0)

    The returned `Match`s by this pattern will have group strings
    .group('name') and .group('value')
    Returns
        `re.Pattern` object
    """
    return re.compile(_TAG_PATTERN.format(name=name, value=value), flags=flags)


class ScriptTag(Enum):
    AFFECTED = "affected"
    CREATION_DATE = "creation_date"
    CVSS_BASE = "cvss_base"
    CVSS_BASE_VECTOR = "cvss_base_vector"
    DEPRECATED = "deprecated"
    IMPACT = "impact"
    INSIGHT = ("insight",)
    LAST_MODIFICATION = "last_modification"
    QOD = "qod"
    QOD_TYPE = "qod_type"
    SEVERITY_VECTOR = "severity_vector"
    SEVERITY_ORIGIN = "severity_origin"
    SEVERITY_DATE = "severity_date"
    SOLUTION = "solution"
    SOLUTION_TYPE = "solution_type"
    SUMMARY = "summary"
    VULDETECT = "vuldetect"


# pylint: disable=invalid-name
__script_tag_pattern = None

__DATE_VALUE = r"[A-Za-z0-9\:\-\+\,\s\(\)]{44}"

__script_tag_values = {
    ScriptTag.DEPRECATED: r"TRUE",
    ScriptTag.CVSS_BASE_VECTOR: r"AV:[LAN]/AC:[HML]/Au:[NSM]/C:[NPC]/I:"
    r"[NPC]/A:[NPC]",
    ScriptTag.CVSS_BASE: r"(10\.0|[0-9]\.[0-9])",
    ScriptTag.CREATION_DATE: __DATE_VALUE,
    ScriptTag.LAST_MODIFICATION: __DATE_VALUE,
}


def init_script_tag_patterns() -> None:
    # pylint: disable=global-statement
    global __script_tag_pattern

    __script_tag_pattern = dict()

    for tag in ScriptTag:
        flags = 0
        value = __script_tag_values.get(tag)

        if value is None:
            value = r".+?"
            flags = re.MULTILINE | re.DOTALL

        __script_tag_pattern[tag] = _get_tag_pattern(
            name=tag.value, value=value, flags=flags
        )


def get_script_tag_patterns() -> Dict[ScriptTag, re.Pattern]:
    if not __script_tag_pattern:
        init_script_tag_patterns()

    return __script_tag_pattern


def get_script_tag_pattern(script_tag: ScriptTag) -> re.Pattern:
    script_tag_patterns = get_script_tag_patterns()
    return script_tag_patterns[script_tag]


_SPECIAL_TAG_PATTERN = (
    r'script_(?P<name>{name})\s*\(["\']?(?P<value>{value})["\']?\s*\)\s*;'
)


class SpecialScriptTag(Enum):
    ADD_PREFERENCE = "add_preference"
    BUGTRAQ_ID = "bugtraq_id"
    CATEGORY = "category"
    COPYRIGHT = "copyright"
    CVE_ID = "cve_id"
    DEPENDENCIES = "dependencies"
    EXCLUDE_KEYS = "exclude_keys"
    FAMILY = "family"
    MANDATORY_KEYS = "mandatory_keys"
    NAME = "name"
    OID = "oid"
    REQUIRE_KEYS = "require_keys"
    REQUIRE_PORTS = "require_ports"
    REQUIRE_UDP_PORTS = "require_udp_ports"
    VERSION = "version"
    XREF = "xref"


def _get_special_tag_pattern(
    name: str, *, value: str = r".+?", flags: re.RegexFlag = 0
) -> re.Pattern:
    return re.compile(
        _SPECIAL_TAG_PATTERN.format(name=name, value=value), flags=flags
    )


# pylint: disable=invalid-name
__special_script_tag_patterns = None


def init_special_script_tag_patterns() -> None:
    # pylint: disable=global-statement
    global __special_script_tag_patterns

    __special_script_tag_patterns = dict()
    for tag in SpecialScriptTag:
        if tag.value == "xref":
            __special_script_tag_patterns[tag] = re.compile(
                _XREF_TAG_PATTERN.format(
                    name=tag.value, value=r".+?", type="URL"
                ),
            )
        elif tag.value == "oid":
            __special_script_tag_patterns[tag] = _get_special_tag_pattern(
                name=tag.value, value=r'\s*["\'](?P<oid>([0-9.]+))["\']\s*'
            )
        elif tag.value == "version":
            __special_script_tag_patterns[tag] = _get_special_tag_pattern(
                name=tag.value, value=r"[0-9\-\:\+T]{24}"
            )
        else:
            __special_script_tag_patterns[tag] = _get_special_tag_pattern(
                name=tag.value, flags=re.MULTILINE
            )


def get_special_script_tag_patterns() -> Dict[SpecialScriptTag, re.Pattern]:
    if not __special_script_tag_patterns:
        init_special_script_tag_patterns()

    return __special_script_tag_patterns


def get_special_script_tag_pattern(
    special_script_tag: SpecialScriptTag,
) -> re.Pattern:
    special_script_tag_patterns = get_special_script_tag_patterns()
    return special_script_tag_patterns[special_script_tag]


def get_special_tag_pattern(
    name: SpecialScriptTag,
    *,
    value: str = None,
    flags: re.RegexFlag = 0,
    url_type: str = "URL",
) -> re.Pattern:
    """
    The returned pattern catchs all `script_<name>(<value>);`

    Arguments:
        name        script tag name
        value       script tag value (default: at least on char)
        flags       regex flags for compile (default: 0)

    The returned `Match`s by this pattern will have group strings
    .group('name') and .group('value')
    Returns
        `re.Pattern` object
    """
    # if not value:
    #     return SpecialScriptTagPatterns().pattern[name.value]
    if name.value == "x_ref":
        return re.compile(
            _XREF_TAG_PATTERN.format(
                name=name.value, value=value, type=url_type
            ),
            flags=flags,
        )
    return _get_special_tag_pattern(name=name.value, value=value, flags=flags)


class CommonScriptTagsPattern:
    instance = False

    def __init__(self) -> None:
        self.pattern = _get_tag_pattern(
            name=r"(summary|impact|affected|insight|vuldetect|solution)",
            flags=re.MULTILINE,
        )
        self.instance = self


def get_common_tag_patterns() -> re.Pattern:
    if CommonScriptTagsPattern.instance:
        return CommonScriptTagsPattern.instance.pattern
    return CommonScriptTagsPattern().pattern
