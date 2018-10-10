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

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QGraphicsScene

import numpy as np
from astropy.io import fits

from stellate_ui import Ui_MainWindow


class StellateMainWindow(QMainWindow):
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

        # Create a scene for the viewer
        self.scene = QGraphicsScene()
        self.ui.imgViewer.setScene(self.scene)

        # Add viewer mouse callbacks

        # Menu callbacks
        self.ui.actionOpen_FITS.triggered.connect(self.choose_fits)

    def choose_fits(self):
        """
        Let use choose a FITS file to load
        :return:
        """

        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog

        # Open a file chooser dialog
        fileName, _ = QFileDialog.getOpenFileName(self,
            "QFileDialog.getOpenFileName()",
            "",
            "All Files (*);;FITS images (*.fit)",
            options=options)

        if fileName:
            self.load_fits(fileName)

    def load_fits(self, fileName):
        """
        Load the FITS file selected by the user
        :param fileName:
        :return:
        """

        with fits.open(fileName) as self.hdu_list:

            # Load image data from FITS
            self.img16 = self.hdu_list[0].data

        # Robust scaling to 95 percentile
        p95 = np.percentile(self.img16, 100.0)
        imin, imax = 0, p95
        self.img16[self.img16 > p95] = p95

        # Scale the image from uint16 to uint8 for display
        self.img8 = np.uint8((self.img16 - imin) / float(imax) * 255.0)

        # Convert the uchar grayscale image to a pixmap
        w, h = self.img8.shape[1], self.img8.shape[0]
        qimage = QImage(self.img8, w, h, QImage.Format_Grayscale8)
        qpixmap = QPixmap(qimage)

        # Add the pixmap to the graphics scene
        try:
            self.scene.addPixmap(qpixmap)
        except Exception as err:
            print(str(err))

    def zoom_image(self):

        pass

    def pan_image(self):

        pass



# Main entry point
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = StellateMainWindow()
    window.show()

    sys.exit(app.exec_())

