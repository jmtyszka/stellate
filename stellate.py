#!/usr/bin/env python3
"""
Simple FITS astronomy viewer/processor

AUTHOR
----
Mike Tyszka, Ph.D.

DATES
----
2018-10-08 JMT From scratch

LICENSE
----

This file is part of Stellate.

Stellate is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Stellate is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with stellate.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import numpy as np
from PyQt5 import QtWidgets
from astropy.io import fits
from stellate_ui import Ui_MainWindow
from starfinder import starfinder


class StellateMainWindow(QtWidgets.QMainWindow):
    """
    Single inheritance class for Stellate UI
    See http://pyqt.sourceforge.net/Docs/PyQt5/designer.html
    """

    def __init__(self):

        # Init the base class
        super().__init__()

        # Set up the Qt Designer-generated UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.img16 = np.array([])

        # Menu callbacks
        self.ui.actionOpen_FITS.triggered.connect(self.choose_fits)

        # Button callbacks
        self.ui.actionAutoStretch.triggered.connect(self.autostretch)
        self.ui.actionFindStars.triggered.connect(self.findstars)

    def choose_fits(self):
        """
        Open file chooser to select FITS file(s)

        :return:
        """

        options = QtWidgets.QFileDialog.Options()

        # Open a file chooser dialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
            "QFileDialog.getOpenFileName()",
            "",
            "All Files (*);;FITS images (*.fit)",
            options=options)

        if fileName:
            self.load_fits(fileName)

    def load_fits(self, fileName):

        # Load FITS image from file
        with fits.open(fileName) as hdu_list:
            self.img16 = hdu_list[0].data

        # Pass uint16 image to the viewer
        self.ui.viewer.setImage(self.img16)

    def autostretch(self):
        # Pass Auto Stretch button status to viewer and repaint
        self.ui.viewer.autostretch(self.ui.autoStretchButton.isChecked())

    def findstars(self):
        # Trigger a star search in the current image
        if self.img16.size > 0:
            starfinder(self.img16)

# Main entry point
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = StellateMainWindow()
    window.show()

    sys.exit(app.exec_())

