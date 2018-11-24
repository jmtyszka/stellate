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
from skimage.io import imsave
from skimage.measure import ransac
from skimage.transform import AffineTransform, PolynomialTransform, warp


class AstroStack():

    def __init__(self, fnames=[], in_mem=True):

        # Public attributes (get and set)
        self.ref_index = 0

        # Protected attributes
        self._fnames = fnames
        self._stack = []

        # Load images into a list of AstroImages
        for fname in fnames:
            print('  Loading FITS image from %s' % fname)
            self._stack.append(AstroImage(fname, in_mem))

    def __len__(self):
        return len(self._stack)

    def register(self):

        print('')
        print('Image stack registration')

        if len(self) <= 1:
            print('  More than one image required for stack registration - returning')
            return

        # Fixed reference starfield
        stars_fixed = self._stack[self.ref_index].stars(write_sidecar=True)

        for aimg in self._stack:

            stars_moving = aimg.stars(write_sidecar=True)

            # Calculate transform mapping the moving starfield to the reference starfield
            T, inliers = self.calc_transform(stars_moving, stars_fixed)

            # Set astroimage transform
            aimg.set_transform(T)

            # Summarize transform
            print('')
            print('RANSAC Affine Transform Results')
            print('  Displacement : (%0.1f, %0.1f) pixels' % (T.translation[0], T.translation[1]))
            print('  Rotation     : %0.1f degrees' % np.rad2deg(T.rotation))
            print('  Inlier Count : %d' % np.sum(inliers))

    def calc_transform(self, stars_moving, stars_fixed):
        """
        Calculate the transform mapping a star field to a reference star field using RANSAC

        :param stars_moving: Pandas dataframe, starfield to be moved
        :param stars_fixed: Pandas dataframe, fixed reference starfield
        :return: transform
        """

        # Extract source and reference star centroids as arrays
        moving_all = stars_moving[['cc', 'rc']].values
        fixed_all = stars_fixed[['cc', 'rc']].values

        n_moving, n_fixed = len(moving_all), len(fixed_all)

        # Find out which set is larger - this determines the matching and registration direction
        # Forward : fixed >= moving, map moving (smaller) to fixed
        # Reverse : fixed < moving, map fixed (smaller) to moving
        if n_fixed >= n_moving:
            reverse_mapping = False
            src, dst = self._pair_points(moving_all, fixed_all)
        else:
            reverse_mapping = True
            src, dst = self._pair_points(fixed_all, moving_all)

        # Estimate transform model with RANSAC
        T, inliers = ransac((src, dst),
                            AffineTransform,
                            min_samples=6,
                            residual_threshold=2,
                            max_trials=1000,
                            stop_sample_num=12,
                            stop_probability=0.99)

        # Swap the transform sense if mapping was reversed
        if reverse_mapping:
            T = T.inverse

        return T, inliers

    def _pair_points(self, smaller, larger):
        """
        Find closest matches in the larger set for each point in the smaller set

        :param smaller: array, smaller set of star centroids
        :param larger: array, larger set of star centroids
        :return: src, dst
        """

        n_smaller, n_larger = len(smaller), len(larger)

        # Construct distance matrix (rows: larger  cols: smaller)
        dist = np.zeros([n_larger, n_smaller])
        for rr in range(0, n_larger):
            xl, yl = larger[rr, :]
            for cc in range(0, n_smaller):
                xs, ys = smaller[cc, :]
                dx, dy = xs - xl, ys - yl
                dist[rr, cc] = np.sqrt(dx ** 2 + dy ** 2)

        # Find nearest point in the larger set for each point in the smaller set
        # src : smaller set points
        # dst : larger set matched points
        src = smaller.copy()
        dst = np.zeros([n_smaller, 2])

        for cc in range(0, n_smaller):
            rmin = np.argmin(dist[:, cc])
            dst[cc, :] = larger[rmin, :]

        return src, dst

    def combine(self):

        print('')
        print('Combining images (median)')

        # Loop over all images in stack
        # Resample image using calculated transform
        # Add resampled image to running total

        img_list = []

        for ic, aimg in enumerate(self._stack):

            T = aimg.transform()
            img = aimg.image()

            # Apply transform and resample
            img_tx = warp(img, T, order=3)

            # Add to transformed image list
            img_list.append(img_tx)

        # Convert list to numpy array
        img_array = np.array(img_list)

        # Combine images
        img_comb = np.median(img_array, axis=0)

        # Save combined image to source directory
        dname = os.path.dirname(self._stack[0].filename())
        fname = os.path.join(dname, 'median_combined.png')
        print('Saving combined image to %s' % fname)
        imsave(fname, img_comb)

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


class BicubicTransform(PolynomialTransform):

    def __init__(self):
        super().__init__()

    def estimate(self, src, dst, order=3):
        super().estimate(src, dst, order)

    def residuals(self, src, dst):
        super().residuals(src, dst)
