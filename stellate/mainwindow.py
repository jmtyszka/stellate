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
        self._stack = AstroStack([])

        # Menu callbacks
        self.ui.actionOpen_FITS.triggered.connect(self.load_fits)

        # Button callbacks
        self.ui.actionFindStars.triggered.connect(self.find_stars)
        self.ui.actionRegisterStack.triggered.connect(self.register_stack)

    def load_fits(self):
        """
        Open file chooser to select FITS file(s)

        :return:
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

            # Update image info fields in UI
            self.update_info()

            # Pass first image in FITS stack to the viewer
            img = self._stack.get_img(self._img_idx)
            self.ui.imageViewer.set_image(img)

    def update_info(self):

        ii = self._img_idx
        fname = self._stack.get_fname(ii)

        self.ui.fnameText.setText(fname)
        self.ui.indexText.setText('%d of %d' % (ii+1, len(self._stack)))

        hdr = self._stack.get_hdr(ii)

        # TODO: Setup a FITS header parse that handles missing tags
        self.ui.targetText.setText(hdr['OBJECT'])
        self.ui.dimText.setText('%d x %d' % (hdr['NAXIS1'], hdr['NAXIS2']))

    def find_stars(self):

        stars_df = self._stack.get_stars(self._img_idx)
        self.ui.imageViewer.show_stars(stars_df)

    def register_stack(self):
        self._stack.register()

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

            # Update displayed image in viewer
            self.ui.imageViewer.set_image(self._stack.get_img(self._img_idx))

