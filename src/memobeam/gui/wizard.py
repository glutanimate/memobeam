# -*- coding: utf-8 -*-

# MemoBeam Add-on for Anki
#
# Copyright (C) 2019  Glutanimate <https://glutanimate.com/>
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
MemoBeam wizard dialog
"""

import random
import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel, QWizard, QWidget

from aqt.utils import askUser

from .contrib import invokeContributionsDialog
from .forms import wizard as qtform_wizard

memories = (
    "That <b>cringy moment</b> in school that you always think about before going to sleep",
    "That <b>earworm</b> that's been annoying you recently",
    "246 <b>internet memes</b> that are no longer relevant or funny",
    "That <b>dreadful movie</b> you saw last year",
    "The <b>terrible last season</b> of that TV show",
    "That time you did that <b>embarassing thing</b> in public",
    "Intricate knowledge of <b>3 mobile games</b> you never intend to play again",
)


class ProgressThread(QThread):
    """
    Runs a counter thread.
    """

    countChanged = pyqtSignal(int)
    countDone = pyqtSignal()
    countInterrupt = pyqtSignal()

    def __init__(self, *args, **kwargs):
        self._is_running = self._is_paused = False
        super(ProgressThread, self).__init__(*args, **kwargs)

    def run(self):
        self._is_running = True
        count = 0
        step = 0.1
        while count < 10:
            if not self._is_running:
                return
            if self._is_paused:
                time.sleep(1)
                continue
            count += step
            if count == 5:
                self.countInterrupt.emit()
                self.pause()
                continue
            count = round(count, 2)
            time.sleep(step)
            self.countChanged.emit(count * 10)
        self.countDone.emit()

    def stop(self):
        self._is_running = False

    def pause(self):
        self._is_paused = True

    def unpause(self):
        self._is_paused = False


class BeamWizard(QWizard):
    def __init__(self, deck: str, cards: int, year: int, parent: QWidget = None):
        super(BeamWizard, self).__init__(parent=parent)
        self.deck = deck
        self.cards = cards
        self.year = year
        self._complete = True
        self.pThread = None
        self.form = qtform_wizard.Ui_Dialog()
        self.form.setupUi(self)
        self.setOption(QWizard.NoBackButtonOnLastPage, True)
        self._setupUI()

    def _setupUI(self):
        self.movie = QMovie(":/memobeam/icons/transfer.gif")
        self.formatLabel(self.form.labelYear)
        self.formatLabel(self.form.labelDeck)
        self.formatLabel(self.form.labelDone)
        self.form.labelTransfer.setMovie(self.movie)
        self.form.btnContrib.clicked.connect(lambda: invokeContributionsDialog(self))

    def formatLabel(self, label: QLabel):
        fdict = {"NextYear": self.year + 1, "Cards": self.cards, "Deck": self.deck}
        text = label.text().format(**fdict)
        label.setText(text)

    def onBeamInProgress(self):
        self._complete = False
        self.movie.start()
        self.pThread = ProgressThread()
        self.pThread.countChanged.connect(self.onCountChanged)
        self.pThread.countDone.connect(self.onBeamDone)
        self.pThread.countInterrupt.connect(self.onBeamInterrupted)
        self.pThread.start()
        self.form.labelProgress.setText("Beaming flashcards into memory...")

    def onCountChanged(self, val: int):
        self.form.progressBar.setValue(val)

    def onBeamDone(self):
        self._complete = True
        self.form.labelProgress.setText("Done!")
        self.movie.stop()
        self.currentPage().completeChanged.emit()
        self.next()

    def onBeamInterrupted(self):
        self.movie.stop()
        memsamples = random.sample(memories, 3)

        q = """
<b>Warning</b>: It seems like your long-term memory is <b>running out of space</b>. 
MemoBeam has identified a number of <b>obsolete memories</b> it could delete
to make some more room:
<ul>
{}
</ul>
Would you be OK with <b>deleting</b> these memories?
""".format(
            "\n".join("<li>{}</li>".format(i) for i in memsamples)
        )

        a = askUser(q, parent=self, title="MemoBeam")
        if not a:
            self.back()
            return
        self.movie.start()
        self.form.labelProgress.setText(
            "Deleting unneeded memories and continuing with beaming..."
        )
        self.pThread.unpause()

    def initializePage(self, pid: int):
        super(BeamWizard, self).initializePage(pid)
        if pid == 3:
            self.onBeamInProgress()
        pass

    def cleanup(self):
        if self.pThread:
            self.pThread.stop()

    def accept(self):
        self.cleanup()
        super(BeamWizard, self).accept()

    def reject(self):
        self.cleanup()
        super(BeamWizard, self).reject()
