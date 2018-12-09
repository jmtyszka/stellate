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

import os
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
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

        # Init image stack
        self._n_imgs = 0
        self._img_idx = 0
        self._stack = AstroStack()

        # Init LRGB short stack
        self._lrgb = AstroStack(nimgs=4)

        # Inclusion criteria
        self._max_diam = 100.0
        self._min_circ = 0.0

        # Menu callbacks
        self.ui.actionOpen_FITS.triggered.connect(self.load_fits)

        # Text field callbacks
        self.ui.actionRefIndex.triggered.connect(self._set_ref_index)
        self.ui.actionImageIndex.triggered.connect(self._set_image_index)
        self.ui.actionMaxDiam.triggered.connect(self._set_max_diam)
        self.ui.actionMinCirc.triggered.connect(self._set_min_circ)

        # Stack tab slider callbacks
        self.ui.maxLevelSlider.sliderReleased.connect(self.update_stack_viewer)
        self.ui.minLevelSlider.sliderReleased.connect(self.update_stack_viewer)

        # Stack tab button callbacks
        self.ui.actionFindStars.triggered.connect(self.find_stars)
        self.ui.actionRegisterStack.triggered.connect(self.register_stack)
        self.ui.actionAverageStack.triggered.connect(self.combine_stack)

        # LRGB tab button callbacks
        self.ui.loadLumButton.released.connect(lambda: self.load_lrgb(0))
        self.ui.loadRedButton.released.connect(lambda: self.load_lrgb(1))
        self.ui.loadGreenButton.released.connect(lambda: self.load_lrgb(2))
        self.ui.loadBlueButton.released.connect(lambda: self.load_lrgb(3))

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
            self._stack = AstroStack(fnames=fnames)

            # Reset current image index
            self._img_idx = 0

            # Update all tabs dependent on current image
            self.update_ui_text()
            self.update_stack_viewer()

    def load_lrgb(self, idx=0):

        # Setup file dialog options
        options = QtWidgets.QFileDialog.Options()

        # Open a file chooser dialog
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                           directory="",
                                                           filter="PNG images (*.png)",
                                                           options=options)

        if len(fname) > 0:

            # Load selected PNG image into the AstroStack at the given index
            self._lrgb.load_png(fname, idx)
            self.update_lrgb()

    def update_stack_viewer(self):
        """
        Update image displayed in the stack viewer
        """

        # Get current astroimage from stack
        aimg = self._stack.astroimage(self._img_idx)

        # Pass astroimage and scale settings to image viewer
        self.ui.StackViewer.set_image(aimg, self.scale_settings())

    def update_lrgb(self):
        """
        Update LRGB color image
        """

        self.ui.LRGBViewer.render_lrgb(self._lrgb)

    def update_ui_text(self):

        ii = self._img_idx
        fname = self._stack.filename(ii)

        # Update UI text fields
        self.ui.fnameText.setText(fname)
        self.ui.indexText.setText('%d' % (ii+1))
        self.ui.maxIndexText.setText('%d' % len(self._stack))
        self.ui.refIndexText.setText('%d' % (self._stack.ref_index+1))

        # Update the metadata display
        self.ui.FITSMetaText.show_metadata(self._stack.metadata(ii))

    def scale_settings(self):
        """
        Pull scale min, max and mode from UI
        """

        # Sliders range from 0.0 to 100.0 in 1.0 steps
        smin = self.ui.minLevelSlider.value()
        smax = self.ui.maxLevelSlider.value()

        # Set min max text boxes
        self.ui.minLevelText.setText('%d' % smin)
        self.ui.maxLevelText.setText('%d' % smax)

        self._scale_settings = smin, smax

        return self._scale_settings

    def find_stars(self):

        stars_df = self._stack.stars(self._img_idx)
        self.ui.StackViewer.show_stars(stars_df)

    def register_stack(self):
        if len(self._stack) > 0:
            self._stack.register(self.ui.registerProgressBar)
            self.update_register()

    def combine_stack(self):
        if len(self._stack) > 0:
            self._stack.combine(self._max_diam, self._min_circ, self.ui.registerProgressBar)

    def update_register(self):
        """
        Clear and refill the registration table from the astroimage stack

        :return:
        """

        regtab = self.ui.registrationTable

        # Clear table of any previous entries
        regtab.clear()
        regtab.setHorizontalHeaderLabels(['Star Count', 'Avg Diam', 'Avg Circ', 'X Disp', 'Y Disp', 'Rotation', 'Filename'])

        # Make space for registration results
        n_imgs = len(self._stack)
        regtab.setRowCount(n_imgs)

        for ic in range(0, n_imgs):

            aimg = self._stack.astroimage(ic)

            # Pull information for registration table
            fname = os.path.basename(aimg.filename())
            n_stars = aimg.num_stars()
            avg_diam = aimg.mean_star_diameter()
            avg_circ = aimg.mean_star_circularity()
            T = aimg.transform()
            dx, dy = T.translation
            rot = np.rad2deg(T.rotation)

            # Set row background color depending on image status (ref, excluded, etc)
            if avg_diam > self._max_diam or avg_circ < self._min_circ:
                bgcolor = QtGui.QColor(250, 220, 200)
            else:
                bgcolor = QtGui.QColor(255, 255, 255)

            if ic == self._stack.ref_index:
                bgcolor = QtGui.QColor(220, 250, 220)

            # Fill row
            self._set_table_item(regtab, ic, 0, '%d' % n_stars, bgcolor)
            self._set_table_item(regtab, ic, 1, '%0.3f' % avg_diam, bgcolor)
            self._set_table_item(regtab, ic, 2, '%0.3f' % avg_circ, bgcolor)
            self._set_table_item(regtab, ic, 3, '%0.3f' % dx, bgcolor)
            self._set_table_item(regtab, ic, 4, '%0.3f' % dy, bgcolor)
            self._set_table_item(regtab, ic, 5, '%0.3f' % rot, bgcolor)
            self._set_table_item(regtab, ic, 6, fname, bgcolor)

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
            self.update_ui_text()

            # Update displayed image in viewer
            self.ui.StackViewer.set_image(self._stack.astroimage(self._img_idx), self.scale_settings())

    # Internal methods

    def _set_table_item(self, regtab, row, col, text, bgcolor=QtGui.QColor(255, 255, 255)):

        qitem = QtWidgets.QTableWidgetItem(text)
        qitem.setTextAlignment(QtCore.Qt.AlignHCenter)
        qitem.setBackground(bgcolor)
        regtab.setItem(row, col, qitem)

    def _set_ref_index(self):

        ref_txt = self.ui.refIndexText.text()

        if ref_txt.isdigit():
            new_ref = int(ref_txt) - 1
            new_ref = np.clip(new_ref, 0, len(self._stack) - 1)
        else:
            new_ref = 0

        self._stack.ref_index = int(new_ref)
        self.ui.refIndexText.setText('%d' % (new_ref + 1))

    def _set_image_index(self):

        idx_txt = self.ui.indexText.text()

        if idx_txt.isdigit():
            new_idx = int(idx_txt) - 1
            new_idx = np.clip(new_idx, 0, len(self._stack) - 1)
        else:
            new_idx = 0

        self._stack.ref_index = int(new_idx)
        self.ui.refIndexText.setText('%d' % (new_idx + 1))

    def _set_max_diam(self):

        max_diam = self.ui.maxAvgDiamText.text()
        if self._isfloat(max_diam):
            self._max_diam = float(max_diam)
        else:
            self._max_diam = 100.0
        self.ui.maxAvgDiamText.setText('%0.1f' % self._max_diam)
        self.update_register()

    def _set_min_circ(self):

        min_circ = self.ui.minAvgCircText.text()
        if self._isfloat(min_circ):
            self._min_circ = float(min_circ)
        else:
            self._min_circ = 0.0
        self.ui.minAvgCircText.setText('%0.1f' % self._min_circ)
        self.update_register()

    def _isfloat(self, float_str):
        try:
            num = float(float_str)
        except ValueError:
            return False
        return True
