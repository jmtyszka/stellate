#!/usr/bin/env python3
"""
Image viewer subclass of PyQtGraph PlotItem

AUTHOR
----
Mike Tyszka, Ph.D.

DATES
----
2018-10-08 JMT Implement using PyQt5 QGraphicsView
2018-11-07 JMT Reimplement using PyQtGraph widget

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

from skimage.exposure import rescale_intensity
from stellate.starfinder import *

from pyqtgraph.Qt import QtGui, QtWidgets
import pyqtgraph as pg


class imageviewer(pg.GraphicsView):

    def __init__(self, central_widget):

        # Init the base class
        super().__init__()

        self._layout = pg.GraphicsLayout()
        self.setCentralItem(self._layout)
        self.show()

        self._img_box = pg.ViewBox()
        self._img_box.setAspectLocked(True)
        self._layout.addItem(self._img_box)

        # Create a noise image as a placeholder
        self._img = np.random.normal(size=(3100, 2100))
        self._img_item = pg.ImageItem(self._img)
        self._img_box.addItem(self._img_item)
        self._has_image = True

        # Add histogram with range bars below image
        self._hist_item = pg.PlotItem()
        self._hist_item.setFixedHeight(64)
        self._hist_item.hideAxis('left')
        self._layout.addItem(self._hist_item, 1, 0)

        # Add limit sliders to histogram
        self._hlims_item = pg.LinearRegionItem()
        self._hist_item.addItem(self._hlims_item)

        # Connect limit slider signals to image contrast adjustment
        self._hlims_item.sigRegionChangeFinished.connect(self.update_image)

    def set_image(self, img=None):

        if img.any():
            self._has_image = True
            self._img = img.copy()
            self.update_histogram()
            self.update_image()
        else:
            self._has_image = False

    def update_histogram(self):

        if self._has_image:

            # Fill histogram
            f, x = np.histogram(self._img, 1000)
            self._hist_item.plot(x, f, stepMode=True, fillLevel=0, brush=(0,0,255,150))

            # Reset intensity limits
            self._hlims_item.setRegion((np.min(x), np.max(x)))

    def update_image(self):

        if self._has_image:

            # Get intensity limits from histogram limit sliders
            ilims = self._hlims_item.getRegion()

            # Rescale image intensities
            img_adj = rescale_intensity(self._img, in_range=ilims, out_range='uint8')

            # Replace image data in image item
            self._img_item.setImage(img_adj.transpose())

    def show_stars(self, stars):
        #
        # for s in stars:
        #
        #     bb = s.bbox
        #     x, y = bb[1], bb[0]
        #     w, h = bb[3]-bb[1], bb[2]-bb[0]
        #
        #     # Green bbox, width 1
        #     star_rect = QtWidgets.QGraphicsRectItem(x, y, w, h)
        #     pen = QPen(QColor('#00FF00'), 1)
        #     star_rect.setPen(pen)
        #
        #     # Add bbox to star overlay group
        #     self._staroverlay.addToGroup(star_rect)
        pass
