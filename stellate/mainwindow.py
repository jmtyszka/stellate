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

import numpy as np
from PyQt5 import QtWidgets, QtCore
from stellate.stellate_ui import Ui_MainWindow
from stellate.astrostack import AstroStack


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
        self._n_imgs = 0
        self._img_idx = 0
        self._stack = AstroStack()

        # Menu callbacks
        self.ui.actionOpen_FITS.triggered.connect(self.load_fits)

        # Button callbacks
        self.ui.actionFindStars.triggered.connect(self.find_stars)
        self.ui.actionRegisterStack.triggered.connect(self.register_stack)
        self.ui.actionAverageStack.triggered.connect(self.combine_stack)

    def load_fits(self):
        """
        Select and load one or more FITS images
        """

        # Setup file dialog options
        options = QtWidgets.QFileDialog.Options()

        # Open a multifile chooser dialog
        fnames, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
            directory="",
            filter="FITS images (*.fit;*.fits)",
            options=options)

        if len(fnames) > 0:

            # Load selected FITS images into an AstroStack object
            self._stack = AstroStack(fnames)

            # Reset current image index
            self._img_idx = 0

            # Update all tabs dependent on current image
            self.update_metatext()
            self.update_viewer()

    def update_viewer(self):
        """
        Update image displayed in the image viewer
        """

        # Get current astroimage from stack
        aimg = self._stack.astroimage(self._img_idx)

        # Pass astroimage and scale settings to image viewer
        self.ui.imageViewer.set_image(aimg, self.scale_settings())

    def update_metatext(self):

        ii = self._img_idx
        fname = self._stack.filename(ii)

        self.ui.fnameText.setText(fname)
        self.ui.indexText.setText('%d of %d' % (ii+1, len(self._stack)))

        # Update the metadata display
        self.ui.FITSMetaText.show_metadata(self._stack.metadata(ii))

    def scale_settings(self):
        """
        Pull scale min, max and mode from UI
        """

        # Sliders range from 0.0 to 100.0 in 1.0 steps
        smin = self.ui.minLevelSlider.value()
        smax = self.ui.maxLevelSlider.value()
        sperc = self.ui.percentileLevels.isChecked()

        self._scale_settings = smin, smax, sperc

        return self._scale_settings

    def find_stars(self):

        stars_df = self._stack.stars(self._img_idx)
        self.ui.imageViewer.show_stars(stars_df)

    def register_stack(self):
        self._stack.register()

    def combine_stack(self):
        self._stack.combine()

    def keyPressEvent(self, event):
        """
        Handle arrow keys for image number selection

        :param event:
        :return:
        """

        key = event.key()

        if len(self._stack) > 0:

            ni, ii = len(self._stack), self._img_idx

            if key == QtCore.Qt.Key_Up:
                self._img_idx = np.mod(ii + 1, ni)
            elif key == QtCore.Qt.Key_Down:
                self._img_idx = np.mod(ii + ni - 1, ni)
            else:
                pass

            # Update meta data, etc in GUI
            self.update_metatext()

            # Update displayed image in viewer
            self.ui.imageViewer.set_image(self._stack.astroimage(self._img_idx), self.scale_settings())

