#!/usr/bin/env python3
"""
Simple FITS astronomy stacker

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
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from astropy.io import fits
import numpy as np
from skimage import img_as_ubyte


class StellateApp(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        self.ui = uic.loadUi(('stellate.ui'), self)

        # Connect actions to handlers
        self.actionOpen_FITS.triggered.connect(self.chooseFITS)

        self.ui.show()


    def chooseFITS(self):

        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog

        # Open a file chooser dialog
        fileName, _ = QFileDialog.getOpenFileName(self,
            "QFileDialog.getOpenFileName()",
            "",
            "All Files (*);;FITS images (*.fit)",
            options=options)

        if fileName:
            self.loadFITS(fileName)

    def loadFITS(self, fileName):

        with fits.open(fileName) as hdu_list:

            # Load image data from FITS
            img16 = hdu_list[0].data

        # Robust scaling to 95 percentile
        p95 = np.percentile(img16, 95.0)
        imin, imax = 0, p95
        img16[img16 > p95] = p95

        # Display image in Viewer tab
        img8 = np.uint8((img16 - imin) / float(imax) * 255.0)

        # Create

        qimage = QImage(img8, img8.shape[1], img8.shape[0], QImage.Format_Grayscale8)
        pixmap = QPixmap(qimage)
        pixmap = pixmap.scaled(1280, 720, Qt.KeepAspectRatio)
        self.imgViewer.setPixmap(pixmap)


# Main entry point
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = StellateApp()
    window.show()

    sys.exit(app.exec_())

