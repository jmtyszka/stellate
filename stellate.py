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
from PyQt5 import QtWidgets, QtCore
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

        # Init image storage
        self.num_imgs = 0
        self.img_idx = 0
        self.img16_stack = []

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

        # Setup file dialog options
        options = QtWidgets.QFileDialog.Options()

        # Open a multifile chooser dialog
        fnames, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
            directory="",
            filter="FITS images (*.fit)",
            options=options)

        if fnames:
            self.load_fits(fnames)

    def load_fits(self, fnames):
        # Load one or more FITS images into working memory

        print('Attempting to load %d FITS images' % len(fnames))

        # Init image stack
        img_stack = []

        # Load image stack
        for fname in fnames:

            print('  Loading %s' % fname)

            try:
                with fits.open(fname) as hdu_list:
                    img_stack.append(hdu_list[0].data)
            except:
                print('* Problem loading %s - skipping' % fname)

        # Save the image stack in the app
        self.img16_stack = img_stack

        # Pass first image in FITS stack to the viewer
        self.img_idx = 0
        self.num_imgs = len(img_stack)
        self.ui.viewer.setImage(self.img16_stack[self.img_idx], reset=True)

    def autostretch(self):
        # Pass Auto Stretch button status to viewer and repaint
        self.ui.viewer.autostretch(self.ui.autoStretchButton.isChecked())

    def findstars(self):
        # Trigger a star search in the current image
        if self.num_imgs > 0:
            self.stars = starfinder(self.img16_stack[self.img_idx])
            self.ui.viewer.showstars(self.stars)

    def keyPressEvent(self, event):
        """
        Handle main window key presses

        :param event:
        :return:
        """

        key = event.key()

        if self.num_imgs > 0:

            ni, ii = self.num_imgs, self.img_idx

            if key == QtCore.Qt.Key_Up:
                self.img_idx = np.mod(ii + 1, ni)
            elif key == QtCore.Qt.Key_Down:
                self.img_idx = np.mod(ii + ni - 1, ni)
            else:
                pass

            # Update displayed image in viewer
            self.ui.viewer.setImage(self.img16_stack[self.img_idx])


# Main entry point
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = StellateMainWindow()
    window.show()

    sys.exit(app.exec_())

