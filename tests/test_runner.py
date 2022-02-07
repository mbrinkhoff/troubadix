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

from pathlib import Path

from pontos.terminal.terminal import Terminal
from pontos.terminal import _set_terminal
from naslinter.plugin import LinterError, LinterResult

from naslinter.plugins import _PLUGINS
from naslinter.runner import Runner


class TestRunner(unittest.TestCase):
    def setUp(self):
        # store old arguments
        self._term = Terminal()
        _set_terminal(self._term)

    def test_runner_with_all_plugins(self):
        runner = Runner(n_jobs=1, term=self._term)

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
        runner = Runner(
            n_jobs=1,
            term=self._term,
            excluded_plugins=excluded_plugins,
        )

        for plugin in runner.plugins.plugins:
            self.assertIn(plugin.__name__, included_plugins)

    def test_runner_with_included_plugins(self):
        included_plugins = [
            "CheckBadwords",
            "CheckCopyRightYearPlugin",
        ]
        runner = Runner(
            n_jobs=1,
            term=self._term,
            included_plugins=included_plugins,
        )

        for plugin in runner.plugins.plugins:
            self.assertIn(plugin.__name__, included_plugins)

    def test_runner_run_ok(self):
        included_plugins = [
            "UpdateModificationDate",
        ]
        nasl_file = Path(__file__).parent / "plugins" / "test.nasl"
        content = nasl_file.read_text(encoding="latin1")

        runner = Runner(
            n_jobs=1,
            term=self._term,
            included_plugins=included_plugins,
        )

        results = runner.check_file(nasl_file)

        new_content = nasl_file.read_text(encoding="latin1")
        self.assertNotEqual(content, new_content)

        self.assertEqual(len(results.generic_results), 0)
        self.assertEqual(len(results.plugin_results), 1)
        self.assertEqual(
            len(results.plugin_results["update_modification_date"]), 1
        )
        self.assertIsInstance(
            results.plugin_results["update_modification_date"][0], LinterResult
        )

        # revert changes for the next time
        nasl_file.write_text(content, encoding="latin1")

    def test_runner_run_error(self):
        included_plugins = [
            "UpdateModificationDate",
        ]
        nasl_file = Path(__file__).parent / "plugins" / "fail.nasl"
        content = nasl_file.read_text(encoding="latin1")

        runner = Runner(
            n_jobs=1,
            term=self._term,
            included_plugins=included_plugins,
        )

        results = runner.check_file(nasl_file)

        new_content = nasl_file.read_text(encoding="latin1")
        self.assertEqual(content, new_content)

        self.assertEqual(len(results.generic_results), 0)
        self.assertEqual(len(results.plugin_results), 1)
        self.assertEqual(
            len(results.plugin_results["update_modification_date"]), 1
        )

        error = results.plugin_results["update_modification_date"][0]
        self.assertIsInstance(error, LinterError)
        self.assertIn(
            "fail.nasl does not contain a modification day script tag.",
            error.message,
        )
