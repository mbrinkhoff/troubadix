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

import unittest

from naslinter.plugins import _PLUGINS
from naslinter.runner import Runner


class TestRunner(unittest.TestCase):
    def test_runner_with_all_plugins(self):
        runner = Runner()

        plugins = _PLUGINS

        for plugin in runner.plugins.plugins:
            self.assertIn(plugin, plugins)

    def test_runner_with_excluded_plugins(self):
        excluded_plugins = [
            "CheckBadwords",
            "CheckCopyRightYearPlugin",
            "UpdateModificationDate",
        ]
        included_plugins = [
            plugin.__name__
            for plugin in _PLUGINS
            if plugin.__name__ not in excluded_plugins
        ]
        runner = Runner(excluded_plugins=excluded_plugins)

        for plugin in runner.plugins.plugins:
            self.assertIn(plugin.__name__, included_plugins)

    def test_runner_with_included_plugins(self):
        included_plugins = [
            "CheckBadwords",
            "CheckCopyRightYearPlugin",
        ]
        runner = Runner(included_plugins=included_plugins)

        for plugin in runner.plugins.plugins:
            self.assertIn(plugin.__name__, included_plugins)
