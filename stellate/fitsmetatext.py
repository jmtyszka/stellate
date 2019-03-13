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

import string
from PySide2.QtWidgets import QTextEdit


class FITSMetaText(QTextEdit):

    def __init__(self, central_widget):

        # Init the base class
        super().__init__()

        # Set to read only
        self.setReadOnly(True)

        # Setup HTML template
        self._init_template()

    def show_metadata(self, metadata=None):

        if len(metadata) < 1:
            print('* show_fits: Empty header - returning')
            return

         # Construct substitution dictionary for HTML report
        qc_dict = dict([
            ('acq_date_loc', metadata['AcqDateLocal']),
            ('acq_date_utc', metadata['AcqDateUTC']),
            ('object', metadata['Object']),
            ('nx', metadata['Width']),
            ('ny', metadata['Height']),
            ('sensor', metadata['Sensor']),
            ('sensor_temp', metadata['SensorTemperature']),
            ('exposure', metadata['Exposure']),
            ('gain', metadata['Gain']),
            ('egain', metadata['EGain']),
            ('offset', metadata['Offset']),
        ])

        # Generate HTML report from template (see above)
        self._html_template = string.Template(self._html_template_format)
        html_data = self._html_template.safe_substitute(qc_dict)

        # Pass HTML to text widget
        self.setHtml(html_data)

    def _init_template(self):

        self._html_template_format = """
        <html>
        <head>
        <STYLE TYPE="text/css">
        BODY { font-family : arial, sans-serif; }
        td, th {
          padding-left : 10px;
          padding-right  : 10px;
          padding-top    : 0px;
          padding-bottom : 0px;
          text-align     : "left";
        }
        </STYLE>
        </head>

        <body>
        <h1 style="background-color:#E0E0FF">FITS Header Metadata</h1>

        <h2> General </h2>
        <div>
            <table>
                <tr> <td> Object <td> $object </tr>
                <tr> <td> Acquisition Date (UTC) <td> $acq_date_utc </tr>
                <tr> <td> Acquisition Date (Local) <td> $acq_date_loc </tr>
            </table>
        </div>

        <h2> Sensor Details </h2>
        <div>
            <table>
                <tr> <td> Sensor <td> $sensor </tr>
                <tr> <td> Sensor Temperature <td> $sensor_temp &deg;C</tr>
                <tr> <td> Width <td> $nx pixels </tr>
                <tr> <td> Height <td> $ny pixels </tr>
            </table>
        </div>

        <h2> Capture Details </h2>
        <div>
            <table>
                <tr> <td> Exposure <td> $exposure s</tr>
                <tr> <td> Gain <td> $gain </tr>
                <tr> <td> Offset <td> $offset </tr>
                <tr> <td> e-Gain <td> $egain ADU/e-</tr>
            </table>
        </div>

        </body>
        </html>
        """

