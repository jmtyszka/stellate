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

        # Setup PyQtGraph configuration options
        pg.setConfigOption('antialias', True)
        pg.setConfigOption('imageAxisOrder', 'row-major')

        self._layout = pg.GraphicsLayout()
        self.setCentralItem(self._layout)
        self.show()

        self._image_view = pg.ViewBox()
        self._image_view.setAspectLocked(True)
        self._layout.addItem(self._image_view)

        # Add image item to image view
        self._image_item = pg.ImageItem()
        self._image_view.addItem(self._image_item)
        self._has_image = True

        # Add star tag overlay group
        self._star_tags = QtWidgets.QGraphicsItemGroup()
        self._image_view.addItem(self._star_tags)

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

        dummy_image = np.random.normal(size=(2100, 3100))
        self.set_image(dummy_image)
        self.update_histogram()

    def set_image(self, img=None):

        if img.any():
            self._has_image = True
            self._img = img
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
            img_adj = rescale_intensity(self._img, in_range=ilims, out_range='uint16')

            # Correct for row-col rendering
            # img_adj = np.rot90(img_adj)

            # Replace image data in the ImageItem
            self._image_item.setImage(img_adj, autoDownsample=True)

    def show_stars(self, stars):
        """
        stars is a list of star region properties [rr, cc, diam, circ]
        - rr, cc : row, col of intensity weighted centroid in image space
        - diam   : equivalent circle diameter
        - circ   : region circularity (1.0 = perfect circle)

        :param stars: list of star ROI properties
        :return:
        """

        # Green pen for tags
        pen = QtGui.QPen(QtGui.QColor('#00FF00'), 1)

        # Create a group for the tags
        self._star_tags = QtWidgets.QGraphicsItemGroup()

        for s in stars:

            yy, xx, d, c = s

            r = d * 0.75

            # Tag above
            tag0 = QtWidgets.QGraphicsLineItem(xx, yy+r, xx, yy+2*r)
            tag0.setPen(pen)

            # Tag below
            tag1 = QtWidgets.QGraphicsLineItem(xx, yy-r, xx, yy-2*r)
            tag1.setPen(pen)

            # Tag left
            tag2 = QtWidgets.QGraphicsLineItem(xx-r, yy, xx-2*r, yy)
            tag2.setPen(pen)

            # Tag right
            tag3 = QtWidgets.QGraphicsLineItem(xx+r, yy, xx+2*r, yy)
            tag3.setPen(pen)

            # Add tags to overlay group
            self._star_tags.addToGroup(tag0)
            self._star_tags.addToGroup(tag1)
            self._star_tags.addToGroup(tag2)
            self._star_tags.addToGroup(tag3)

        self._image_view.addItem(self._star_tags)