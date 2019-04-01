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


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


from aqt.qt import *
from aqt.deckbrowser import DeckBrowser

from anki.hooks import addHook

from .libaddon.platform import ANKI20
from .beam import beamIt

def onShowOptions20(self, did):
    m = QMenu(self.mw)
    a = m.addAction(_("Rename"))
    a.connect(a, SIGNAL("triggered()"), lambda did=did: self._rename(did))
    a = m.addAction(_("Options"))
    a.connect(a, SIGNAL("triggered()"), lambda did=did: self._options(did))
    a = m.addAction(_("Export"))
    a.connect(a, SIGNAL("triggered()"), lambda did=did: self._export(did))
    a = m.addAction(_("Delete"))
    a.connect(a, SIGNAL("triggered()"), lambda did=did: self._delete(did))
    # MOD START
    a = m.addAction("Beam it!")
    font = a.font()
    font.setBold(True)
    a.connect(a, SIGNAL("triggered()"), lambda did=did: beamIt(did))
    # MOD END
    m.exec_(QCursor.pos())

def onDeckOptions(menu, did):
    a = menu.addAction("Beam it!")
    a.triggered.connect(lambda b, did=did: beamIt(did))
    font = a.font()
    font.setBold(True)
    a.setFont(font)

def initDeckBrowser():
    if ANKI20:
        # finicky, will break if other add-on tries the same:
        DeckBrowser._showOptions = onShowOptions20
    else:
        addHook("showDeckOptions", onDeckOptions)
