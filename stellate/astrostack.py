#!/usr/bin/env python3
"""
Image registration and combining

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
import numpy as np
from stellate.astroimage import AstroImage
from skimage.io import imread, imsave
from skimage.exposure import rescale_intensity
from skimage.measure import ransac
from skimage.transform import AffineTransform, PolynomialTransform, warp
from PyQt5.QtWidgets import QProgressBar, QApplication

class AstroStack():

    def __init__(self, nimgs=0, fnames=[], in_mem=True):

        # Public attributes (get and set)
        self.ref_index = 0

        # Protected attributes
        self._fnames = fnames

        if nimgs > 0:
            self._stack = [AstroImage()] * nimgs
        else:
            self._stack = []

        # Load images into a list of AstroImages
        for fname in fnames:
            print('  Loading FITS image from %s' % fname)
            self._stack.append(AstroImage(fname, in_mem))

    def __len__(self):
        return len(self._stack)

    def load_png(self, fname, idx=0):

        self._stack[idx] = AstroImage(fname)

    def register(self, progbar=None):

        print('')
        print('Image stack registration')

        if len(self) <= 1:
            print('  More than one image required for stack registration - returning')
            return

        # Fixed reference starfield
        stars_ref = self._stack[self.ref_index].stars(write_sidecar=True)

        for ic, aimg in enumerate(self._stack):

            if progbar:
                pp = ic / float(len(self._stack)) * 100.0
                progbar.setValue(pp)
                QApplication.processEvents()

            stars_ind = aimg.stars(write_sidecar=True)

            # Calculate transform mapping the reference to individual starfields
            T, inliers = self.calc_transform(stars_ref, stars_ind)

            # Set astroimage transform
            aimg.set_transform(T)

            # Summarize transform
            print('')
            print('RANSAC Affine Transform Results')
            print('  Displacement    : (%0.3f, %0.3f) pixels' % (T.translation[0], T.translation[1]))
            print('  Rotation        : %0.3f degrees' % np.rad2deg(T.rotation))
            print('  Inlier Fraction : %0.3f' % (np.sum(inliers)/len(inliers)))

        # Reset progress bar
        if progbar:
            progbar.setValue(0.0)

    def calc_transform(self, stars_ref, stars_ind):
        """
        Calculate the transform mapping the reference to individual starfields using RANSAC

        Note the direction of the optimized transform (ref -> ind) to match the interpolation
        transform required by skimage.transform.warp.

        :param stars_ref: Pandas dataframe, reference starfield
        :param stars_ind: Pandas dataframe, individual starfield
        :return: transform
        """

        # Extract source and reference star centroids as arrays
        ref_all = stars_ref[['xc', 'yc', 'bright']].values
        ind_all = stars_ind[['xc', 'yc', 'bright']].values

        n_ref, n_ind = len(ref_all), len(ind_all)

        # Find out which set is larger for pairing stars
        if n_ind >= n_ref:
            src, dst = self._pair_points(ref_all, ind_all)
        else:
            dst, src = self._pair_points(ind_all, ref_all)

        # Estimate transform model with RANSAC
        T, inliers = ransac((src, dst),
                            AffineTransform,
                            min_samples=6,
                            residual_threshold=2,
                            max_trials=1000,
                            stop_sample_num=12,
                            stop_probability=0.99)

        return T, inliers

    def combine(self, max_diam=100.0, min_circ=0.0, progbar=None):

        print('')
        print('Combining images (median)')

        # Construct image inclusion list
        img_ok = np.zeros(len(self._stack))
        for ic, aimg in enumerate(self._stack):
            img_ok[ic] = aimg.mean_star_diameter() < max_diam and aimg.mean_star_circularity() > min_circ
        img_inc = np.where(img_ok)[0]
        n_ok = len(img_inc)

        # Preallocate memory for registered image array (2D x n_imgs)
        ny, nx = self._stack[0].image().shape

        img_array = np.zeros([ny, nx, n_ok])

        for ic, aic in enumerate(img_inc):

            if progbar:
                pp = ic / float(n_ok) * 100.0
                progbar.setValue(pp)
                QApplication.processEvents()

            aimg = self._stack[aic]

            T = aimg.transform()
            img = aimg.image()

            # Apply transform, resize and store
            img_array[:, :, ic] = warp(img, T, order=3)

        # Combine images
        print('  Median combining registered image stack')
        img_comb = np.median(img_array, axis=2, overwrite_input=True)

        # Condition image for export
        img_png = rescale_intensity(img_comb, out_range='float64')

        # Save combined image to source directory
        dname = os.path.dirname(self._stack[0].filename())
        fname = os.path.join(dname, 'median_combined.png')
        print('Saving combined image to %s' % fname)
        imsave(fname, img_comb)

        # Reset progress bar
        if progbar:
            progbar.setValue(0.0)

    def enforce_size(self):

        # Find maximum height and width of all images in stack
        ny_max, nx_max = 3, 3
        for aimg in self._stack:
            if aimg.has_image():
                ny, nx = aimg.image().shape
                nx_max = nx if nx > nx_max else nx_max
                ny_max = ny if ny > ny_max else ny_max

        print('  Resize all LRGB channels to %d x %d' % (nx_max, ny_max))

        for aimg in self._stack:
            aimg.resize(ny_max, nx_max)

        return ny_max, nx_max

    def filename(self, idx=0):
        if self.idx_in_range(idx):
            fname = self._stack[idx].filename()
        else:
            fname = []
        return fname

    def metadata(self, idx=0):
        if self.idx_in_range(idx):
            md = self._stack[idx].metadata()
        else:
            md = []
        return md

    def astroimage(self, idx=0):
        if self.idx_in_range(idx):
            aimg = self._stack[idx]
        else:
            aimg = []
        return aimg

    def stars(self, idx=0):
        if self.idx_in_range(idx):
            stars = self._stack[idx].stars()
        else:
            stars = []
        return stars

    def idx_in_range(self, idx):
        return idx >= 0 and idx < len(self)

    # Internal methods

    def _pair_points(self, smaller, larger):

        """
        Find closest matches in the larger set for each point in the smaller set.
        Register the brightness-weighted centroids of each starfield before
        determining closest matches.

        :param smaller: array, smaller set of star centroids
        :param larger: array, larger set of star centroids
        :return: src, dst
        """

        n_smaller, n_larger = len(smaller), len(larger)
        xs, ys, bs = smaller[:, 0], smaller[:, 1], smaller[:, 2]
        xl, yl, bl = larger[:, 0], larger[:, 1], larger[:, 2]

        # Weighted centroids
        sbs, sbl = np.sum(bs), np.sum(bl)
        wcx_s, wcy_s = np.dot(xs, bs) / sbs, np.dot(ys, bs) / sbs
        wcx_l, wcy_l = np.dot(xl, bl) / sbl, np.dot(yl, bl) / sbl

        # Register centroids of smaller and larger sets
        dwcx, dwcy = wcx_l - wcx_s, wcy_l - wcy_s
        xs, ys = xs + dwcx, ys + dwcy

        # Construct distance matrix (rows: larger  cols: smaller)
        dist = np.zeros([n_larger, n_smaller])
        for rr in range(0, n_larger):
            xlr, ylr = larger[rr, 0:2]
            for cc in range(0, n_smaller):
                xsc, ysc = smaller[cc, 0:2]
                dx, dy = xsc - xlr, ysc - ylr
                dist[rr, cc] = np.sqrt(dx ** 2 + dy ** 2)

        # Find nearest point in the larger set for each point in the smaller set
        # src : smaller set points
        # dst : larger set matched points
        src = smaller[:, 0:2]
        dst = np.zeros([n_smaller, 2])

        for cc in range(0, n_smaller):
            rmin = np.argmin(dist[:, cc])
            dst[cc, :] = larger[rmin, 0:2]

        return src, dst


class BicubicTransform(PolynomialTransform):

    def __init__(self):
        super().__init__()

    def estimate(self, src, dst, order=3):
        super().estimate(src, dst, order)

    def residuals(self, src, dst):
        super().residuals(src, dst)
