# -*- coding: utf-8 -*-

# MemoBeam Add-on for Anki
#
# Copyright (C)  2019 Glutanimate <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Initializes add-on components.
"""

from PyQt5.QtWidgets import QMenu

from anki.hooks import addHook

from .beam import beam_it


def on_deck_options(menu: QMenu, did: int):
    action = menu.addAction("Beam it!")
    action.triggered.connect(lambda b, did=did: beam_it(did))  # type: ignore
    font = action.font()
    font.setBold(True)
    action.setFont(font)


def initialize_deck_browser():
    try:  # 2.1.20+
        from aqt.gui_hooks import deck_browser_will_show_options_menu

        deck_browser_will_show_options_menu.append(on_deck_options)
    except (ImportError, ModuleNotFoundError):
        addHook("showDeckOptions", on_deck_options)
