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
import pyqtgraph as pg


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

        # Setup intensity histogram
        self.setup_histogram()

    def setup_histogram(self):

        # Get histogram plot item from widget
        pl = self.ui.histogramView.getPlotItem()

        # Add intensity range selector to plot
        x, y = [0, 2^14], [1, 1]
        self.histogram = pl.plot(x, y)
        self.irange_sel = pg.LinearRegionItem()
        pl.addItem(self.irange_sel)

        # Connect selector to image viewer
        self.irange_sel.sigRegionChangeFinished.connect(self.update_image_scaling)

    def update_histogram(self):

        # Construct intensity histogram for current image
        f, x = np.histogram(self.img16_stack[self.img_idx], bins=100)

        self.histogram.setData(x[:-1], f)


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
            filter="FITS images (*.fit;*.fits)",
            options=options)

        if fnames:
            self.load_fits(fnames)

    def load_fits(self, fnames):

        # Init image stack
        img_stack = []

        # Load image stack
        for fname in fnames:

            try:
                with fits.open(fname) as hdu_list:
                    img_stack.append(hdu_list[0].data)
            except:
                self.ui.statusbar.showMessage("* Problem loading %s" % fname)

        self.ui.statusbar.showMessage("Loaded %d FITS images" % len(fnames))

        # Save the image stack in the app
        self.img16_stack = img_stack

        # Pass first image in FITS stack to the viewer
        self.img_idx = 0
        self.num_imgs = len(img_stack)
        self.ui.viewer.set_image(self.img16_stack[self.img_idx], reset=True)

        # Update the intensity histogram
        self.update_histogram()

    def update_image_scaling(self):
        self.ui.viewer.set_scaling('linear', self.irange_sel.getRegion())

    def find_stars(self):

        if self.num_imgs > 0:
            img = self.img16_stack[self.img_idx]
            sbar = self.ui.statusbar
            self.stars = starfinder(img, sbar)
            self.ui.viewer.show_stars(self.stars)

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
            self.ui.viewer.set_image(self.img16_stack[self.img_idx])

