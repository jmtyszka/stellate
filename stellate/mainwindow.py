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
from astropy.io import fits
from stellate.stellate_ui import Ui_MainWindow
from stellate.starfinder import starfinder


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
        self.ui.actionFindStars.triggered.connect(self.find_stars)

    def choose_fits(self):
        """
        Open file chooser to select FITS file(s)

        :return:
        """

        # Setup file dialog options
        options = QtWidgets.QFileDialog.Options()

        # Open a multifile chooser dialog
        self.fnames, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
            directory="",
            filter="FITS images (*.fit;*.fits)",
            options=options)

        if self.fnames:
            self.load_fits()

    def load_fits(self):

        # Init image stack
        self.imgs = []
        self.fits_hdrs = []

        # Load image stack
        for fname in self.fnames:

            try:
                with fits.open(fname) as hdu_list:
                    self.imgs.append(hdu_list[0].data)
                    self.fits_hdrs.append(hdu_list[0].header)
            except:
                self.ui.statusbar.showMessage("* Problem loading %s" % fname)

        self.img_idx = 0
        self.num_imgs = len(self.imgs)

        # Update image info fields in UI
        self.update_info()

        # Pass first image in FITS stack to the viewer
        self.ui.imageViewer.set_image(self.imgs[self.img_idx])

    def update_info(self):

        self.ui.fnameText.setText(self.fnames[self.img_idx])
        self.ui.indexText.setText('%d of %d' % (self.img_idx+1, self.num_imgs))

        hdr = self.fits_hdrs[self.img_idx]

        # TODO: Setup a FITS header parse that handles missing tags
        self.ui.targetText.setText(hdr['OBJECT'])
        self.ui.dimText.setText('%d x %d' % (hdr['NAXIS1'], hdr['NAXIS2']))

    def find_stars(self):

        if self.num_imgs > 0:
            img = self.img16_stack[self.img_idx]
            sbar = self.ui.statusbar
            self.stars = starfinder(img, sbar)
            self.ui.imageViewer.show_stars(self.stars)

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
            self.ui.imageViewer.set_image(self.imgs[self.img_idx])

