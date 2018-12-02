#!/usr/bin/env python3
"""
Locate stars/sources in image

AUTHOR
----
Mike Tyszka, Ph.D.

DATES
----
2018-10-09 JMT From scratch

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
import pandas as pd
import numpy as np
from astropy.io import fits
from numpy.fft import fft2, fftshift
from scipy.optimize import curve_fit
from skimage.morphology import binary_opening, remove_small_objects, white_tophat
from skimage.morphology.selem import disk
from skimage.restoration import estimate_sigma
from skimage.measure import label, regionprops
from skimage.transform import resize, AffineTransform
from skimage.filters import threshold_otsu, gaussian


class AstroImage:

    def __init__(self, fname="", in_mem=True):

        # Filenames
        self._filename = fname
        self._stars_fname = self._replace_ext('_stars.json')

        # FITS data
        self._image = []
        self._fits_header = []

        # Derived image metrics
        self._global_fwhm = -1.0
        self._noise_sd = -1.0
        self._imin = np.nan
        self._imax = np.nan
        self._ipercs = [np.nan, np.nan]

        # Stars in image
        self._stars = pd.DataFrame()
        self._star_mask = []
        self._transform = AffineTransform()

        # Internal status flags
        self._has_image = False
        self._has_stars = False

        # Load FITS image data
        if len(fname) > 0:

            try:
                with fits.open(fname) as hdu_list:
                    self._fits_header = hdu_list[0].header
                    # Load image temporarily to calculate intensity stats
                    self._image = hdu_list[0].data
            except IOError:
                print("* Problem loading %s" % fname)
                return

            # Parse FITS header into astroimage metadata
            self.parse_fits_header()

            # Calculate intensity limits and percentiles
            self.intensity_stats()

            # Keep in memory or purge image data
            if in_mem:
                self._has_image = True
            else:
                self._image = []
                self._has_image = False

    def parse_fits_header(self):

        # Init the metadata dictionary
        md = dict()

        # Start filling fields
        md['AcqDateLocal'] = self._get_card('DATE-LOC')
        md['AcqDateUTC'] = self._get_card('DATE-OBS')
        md['SensorGain'] = self._get_card('GAIN')
        md['Telescope'] = self._get_card('TELESCOP')
        md['Sensor'] = self._get_card('INSTRUME')
        md['SensorTemperature'] = self._get_card('CCD-TEMP')
        md['Dummy'] = self._get_card('DUMMY')
        md['Object'] = self._get_card('TARGET')
        md['Width'] = self._get_card('NAXIS1')
        md['Height'] = self._get_card('NAXIS2')
        md['Exposure'] = self._get_card('EXPOSURE')
        md['Gain'] = self._get_card('GAIN')
        md['Offset'] = self._get_card('OFFSET')

        # Invert EGAIN from e-/ADU to ADU/e-
        md['EGain'] = '%0.3f' % (1.0/float(self._get_card('EGAIN')))

        self._metadata = md

    def stars(self, find_again=False, write_sidecar=False):
        """
        Find likely stars in AP image
        """

        print('')
        print('Star Finder')

        if not self._has_stars:

            if not self._has_image:
                print('* Star Finder: No image loaded - returning')
                return self._stars

            if self._image.size == 0:
                print('* Star Finder: Empty image - returning')
                return self._stars

            # Load available stars file if not recalculating
            if not find_again:
                if os.path.isfile(self._stars_fname):
                    print('  Checking stars sidecar')
                    self.load_stars()
                    if self.num_stars() > 0:
                        print('  Loaded %d stars from sidecar' % self.num_stars())
                        return self._stars
                    else:
                        print('  Empty sidecar - refinding stars')

            ny, nx = self._image.shape

            # Estimate typical star global_fwhm in k-space
            self.estimate_global_fwhm()
            print('  Global global_fwhm estimate : %0.1f pixels' % self._global_fwhm)

            # Matched Gaussian filter (sigma = global_fwhm/2)
            # Low pass filter prior to downsampling
            sigma_g = self._global_fwhm * 0.5
            print('  Gaussian matched filter (sigma = %0.1f pixels' % sigma_g)
            img_gauss = gaussian(self._image, sigma_g)

            # Matched resampling scale factor (global_fwhm = 4 pixels)
            sf = 4.0 / self._global_fwhm

            # Downsample image (bicubic, no antialiasing)
            nxd = int(nx * sf)
            nyd = int(ny * sf)
            print('  Matched resampling to %d x %d' % (nxd, nyd))
            img_dwn = resize(img_gauss, [nyd, nxd], order=3, anti_aliasing=False, mode='reflect')

            # Structuring element on scale of typical star
            # Radius = 5 works well after matched downsampling (empirical)
            star_selem = disk(radius=5)

            # White tophat filter
            # - suppress smooth background
            # - highlight bright objects smaller than selem
            print('  White tophat filtering to highlight stars')
            imgd_wth = white_tophat(img_dwn, star_selem)

            # Global Otsu threshold and remove small objects
            star_maskd = imgd_wth > threshold_otsu(imgd_wth)
            star_maskd = remove_small_objects(star_maskd, min_size=5)

            # Upsample mask to original image dimensions
            # order = 0 -> nearest neighbor
            self._star_mask = np.uint8(resize(star_maskd, [ny, nx], order=0, anti_aliasing=False, mode='reflect'))
            self._has_starmask = True

            # Label connected regions
            print('  Labeling connected regions')
            star_rois = label(self._star_mask)

            # Note future proofing use of row-col coords
            roi_props = regionprops(star_rois, self._image, coordinates='rc')

            # Run through ROIs compiling relevant properties
            star_list = []

            for rp in roi_props:

                # Star centroid in image space (row, col)
                yc, xc = rp.weighted_centroid

                # Estimate star global_fwhm and circularity from intensity ROI
                diam, ecc, circ, bright = self._star_stuff(rp.intensity_image)

                star_list.append([xc, yc, diam, ecc, circ, bright])

            # Convert list of star parameters to a Pandas dataframe
            self._stars = pd.DataFrame(star_list, columns=['xc','yc','diam','ecc', 'circ', 'bright'])

            # Set stars found status
            self._has_stars = True

        # self.prune_stars()

        if write_sidecar:
            self.write_stars()

        return self._stars

    def prune_stars(self):
        """
        Remove outliers and unlikely stars
        """

        # Extract numeric data from dataframe
        bright = self._stars['bright']
        diam = self._stars['diam']
        circ = self._stars['circ']

        # Discard objects larger then 2 * global FWHM
        too_big = diam > self._global_fwhm * 2.0

        # Keep top 25% brightest stars
        too_dim = bright < np.percentile(bright, 75)

        # Discard highly non-circular objects
        not_round = circ < 0.75

        to_drop = np.where(too_big | too_dim | not_round)[0]

        # Prune rows
        self._stars = self._stars.drop(to_drop, axis=0)

    def write_stars(self):
        try:
            print('  Saving stars to %s' % self._stars_fname)
            self._stars.to_json(self._stars_fname)
        except:
            print('* Problem writing stars to %s' % self._stars_fname)

    def load_stars(self):
        try:
            # Read stars to a JSON dataframe
            self._stars = pd.read_json(self._stars_fname)
        except:
            print('* Problem loading stars from %s' % self._stars_fname)
            self._stars = []

    def estimate_noise_sd(self):
        if self._noise_sd < 0.0:
            self._noise_sd = estimate_sigma(self._image)
        return self._noise_sd

    def estimate_global_fwhm(self):
        """
        Estimate mean global_fwhm of bright sources in image in Fourier space
        - circular integrals of abs(k-space)
        - exclude area close to k-space origin
        - model as single Gaussian + dc noise offset (solves baseline issues in [1])

        Refs
        ----
        [1] R. Mizutani et al., “Estimating the resolution of real images,”
        J. Phys. Conf. Ser., vol. 849, no. 1, p. 012042, Jun. 2017 [Online].
        Available: http://iopscience.iop.org/article/10.1088/1742-6596/849/1/012042/meta. [Accessed: 24-Oct-2018]
        """

        if self._global_fwhm < 0.0:

            ask = np.abs(fftshift(fft2(fftshift(self._image))))

            ny, nx = ask.shape

            # Create k-space coordinate mesh
            xv = np.arange(0, nx) - nx * 0.5
            yv = np.arange(0, ny) - ny * 0.5
            xm, ym = np.meshgrid(xv, yv)
            rm = np.sqrt(xm * xm + ym * ym)

            # Skip central region radii (smooth background, nebulosity, etc)
            r_min = 50
            r_max = np.min([nx, ny]) * 0.5

            # Circular integrals around origin
            n_samp = 100
            dr = r_max / float(n_samp)
            rv = np.arange(r_min, r_max, dr)
            Sr = np.zeros_like(rv)

            for ii, rr in enumerate(rv):
                r_mask = (rm > rr) * (rm < (rr + dr))
                Sr[ii] = np.mean(ask[r_mask])

            # Model S(r) as Gaussian + noise baseline

            # Initial guess
            guess = [np.max(Sr), np.mean(rv), 1.0]

            # Fit Gaussian to data
            popt, pcov = curve_fit(self._gauss, xdata=rv, ydata=Sr, p0=guess)

            # Extract star sigma_k estimate
            # Negative sigma_k solutions are possible and valid so take abs
            sigma_k = np.abs(popt[1])

            self._global_fwhm = r_max / sigma_k
            self._has_fwhm = True

        return self._global_fwhm

    def global_fwhm(self):
        return self._global_fwhm

    def set_transform(self, T):
        self._transform = T

    # Getters for protected attributes
    def filename(self):
        return self._filename

    def header(self):
        return self._fits_header

    def image(self):
        return self._image

    def num_stars(self):
        return len(self._stars.index)

    def transform(self):
        return self._transform

    def intensity_stats(self):

        if self._has_image:

            if np.isnan(self._ipercs).any():
                p = np.arange(0.0, 101.0)
                self._ipercs = np.percentile(self._image, p)

            if np.isnan(self._imin):
                self._imin = np.min(self._ipercs)

            if np.isnan(self._imax):
                self._imax = np.max(self._ipercs)

        return self._imin, self._imax, self._ipercs

    def has_image(self):
        return self._has_image

    def has_stars(self):
        return self._has_stars

    def metadata(self):
        return self._metadata

    def mean_star_diameter(self):
        return self._stars['diam'].mean()

    def mean_star_eccentricity(self):
        return self._stars['ecc'].mean()

    def mean_star_circularity(self):
        return self._stars['circ'].mean()

    # Internal methods

    def _gauss(self, x, a, b, c):
        return a * np.exp(-(x / b) ** 2) + c

    def _replace_ext(self, ext_rep):
        root, ext = os.path.splitext(self._filename)
        return root + ext_rep

    def _get_card(self, keyword):
        if keyword in self._fits_header:
            val = str(self._fits_header[keyword])
        else:
            val = ''
        return val

    def _star_stuff(self, roi_img):

        # Otsu threshold ROI star image
        roi_mask = roi_img > threshold_otsu(roi_img)

        # Get binary mask region properties
        roi_props = regionprops(label_image=roi_mask.astype(int), intensity_image=roi_img, coordinates='rc')

        # Init shape metrics
        diam = 0.0
        ecc = 0.0
        circ = 0.0
        bright = 0.0

        for rp in roi_props:

            # Save shape factors for largest diameter region
            # which is assumed to be the star in the ROI
            d = rp.equivalent_diameter

            if d > diam:

                # Save shape factors
                diam = d
                ecc = rp.eccentricity
                area = rp.filled_area
                perim = rp.perimeter
                circ = 4 * np.pi * area / (perim * perim)
                circ = 1.0 if circ > 1.0 else circ
                bright = rp.mean_intensity

        return diam, ecc, circ, bright




