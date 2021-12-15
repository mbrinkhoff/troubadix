# Copyright (C) 2021 Greenbone Networks GmbH
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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass
class LinterResult:
    message: str


class LinterWarning(LinterResult):
    pass


class LinterError(LinterResult):
    pass


class Plugin(ABC):
    name: str = None
    description: str = None


class FileContentPlugin(Plugin):
    @staticmethod
    @abstractmethod
    def run(file_name: str, file_content: str) -> Iterator[LinterResult]:
        pass


class LineContentPlugin(Plugin):
    @staticmethod
    @abstractmethod
    def run(file_name: str, lines: Iterable[str]) -> Iterator[LinterResult]:
        pass
