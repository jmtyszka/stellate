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
from skimage.morphology import remove_small_objects, white_tophat
from skimage.morphology.selem import disk
from skimage.restoration import estimate_sigma
from skimage.measure import label, regionprops
from skimage.transform import resize
from skimage.filters import threshold_otsu, gaussian


class AstroImage:

    def __init__(self, fname, in_mem=True):

        # Filenames
        self._fname = fname
        self._stars_fname = self.replace_ext('_stars.json')

        # FITS data
        self._image = []
        self._fits_hdr = []

        # Derived image metrics
        self._FWHM = -1.0
        self._noise_sd = -1.0

        # Stars in image
        self._stars = pd.DataFrame()
        self._star_mask = []

        # Internal status flags
        self._has_image = False
        self._has_stars = False

        # Load FITS image data
        try:
            with fits.open(fname) as hdu_list:

                self._fits_hdr = hdu_list[0].header

                if in_mem:
                    self._image = hdu_list[0].data
                    self._has_image = True
                else:
                    self._image = []
                    self._has_image = False

        except:
            print("* Problem loading %s" % fname)

    def find_stars(self, find_again=False, write_sidecar=False):
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

            # Estimate typical star FWHM in k-space
            self.estimate_fwhm()
            print('  FWHM estimate : %0.1f pixels' % self._FWHM)

            # Matched Gaussian filter (sigma = FWHM/2)
            # Low pass filter prior to downsampling
            sigma_g = self._FWHM * 0.5
            print('  Gaussian matched filter (sigma = %0.1f pixels' % sigma_g)
            self._image = gaussian(self._image, sigma_g)

            # Matched resampling scale factor (FWHM = 4 pixels)
            sf = 4.0 / self._FWHM

            # Downsample image (bicubic, no antialiasing)
            nxd = int(nx * sf)
            nyd = int(ny * sf)
            print('  Matched resampling to %d x %d' % (nxd, nyd))
            imgd = resize(self._image, [nyd, nxd], order=3, anti_aliasing=False, mode='reflect')

            # Structuring element on scale of typical star
            # Radius = 5 works well after matched downsampling (empirical)
            star_selem = disk(radius=5)

            # White tophat filter
            # - suppress smooth background
            # - highlight bright objects smaller than selem
            print('  White tophat filtering to highlight stars')
            imgd_wth = white_tophat(imgd, star_selem)

            # Global threshold (Yen's method) and remove small objects
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

                r0, c0, _, _ = rp.bbox
                dr, dc = rp.weighted_local_centroid  # (row, col)
                area = np.float(rp.filled_area)  # in pixels
                perim = np.float(rp.perimeter)
                diam = rp.equivalent_diameter

                # Star centroid in image space
                rc, cc = r0 + dr, c0 + dc

                # Circularity [0, 1] with 1.0 = perfect circle
                circ = 4.0 * np.pi * area / (perim * perim)

                star_list.append([rc, cc, diam, circ])

            # Convert list of star parameters to a Pandas dataframe
            self._stars = pd.DataFrame(star_list, columns=['rc','cc','diam','circ'])

            # Set stars found status
            self._has_stars = True

        if write_sidecar:
            self.write_stars()

        return self._stars

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

    def estimate_fwhm(self):
        """
        Estimate mean FWHM of bright sources in image in Fourier space
        - circular integrals of abs(k-space)
        - exclude area close to k-space origin
        - model as single Gaussian + dc noise offset (solves baseline issues in [1])

        Refs
        ----
        [1] R. Mizutani et al., “Estimating the resolution of real images,”
        J. Phys. Conf. Ser., vol. 849, no. 1, p. 012042, Jun. 2017 [Online].
        Available: http://iopscience.iop.org/article/10.1088/1742-6596/849/1/012042/meta. [Accessed: 24-Oct-2018]
        """

        if self._FWHM < 0.0:

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
            popt, pcov = curve_fit(self.gauss, xdata=rv, ydata=Sr, p0=guess)

            # Extract star sigma_k estimate
            # Negative sigma_k solutions are possible and valid so take abs
            sigma_k = np.abs(popt[1])

            self._FWHM = r_max / sigma_k
            self._has_fwhm = True

        return self._FWHM

    def gauss(self, x, a, b, c):
        return a * np.exp(-(x / b) ** 2) + c

    def replace_ext(self, ext_rep):
        root, ext = os.path.splitext(self._fname)
        return root + ext_rep

    # Getters for protected attributes
    def get_fname(self):
        return self._fname

    def get_hdr(self):
        return self._fits_hdr

    def get_img(self):
        return self._image

    def num_stars(self):
        return len(self._stars.index)

