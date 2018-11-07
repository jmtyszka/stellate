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

"""
ORB feature detection and binary descriptor test
"""

import numpy as np
from skimage.morphology import remove_small_objects
from skimage.restoration import estimate_sigma
from skimage.measure import label, regionprops


def starfinder(img16, sbar):
    """
    Find likely stars in AP image

    :param img16: numpy array int16, original AP image
    :return:
    """

    stars = []

    if img16.size == 0:
        print('* Empty image passed to starfinder - returning')
        return stars

    # Estimate noise sd
    sd_n = estimate_sigma(img16, multichannel=False)
    th = 10.0 * sd_n

    # Create superthreshold mask
    mask = img16 > th

    # Remove objects < 9 pixels in size
    sbar.showMessage('Removing small objects', 250)
    mask_clean = remove_small_objects(mask, min_size=9)

    # Label connected regions
    sbar.showMessage('  Labeling connected regions', 250)
    label_image = label(mask_clean)

    # Note future proofing use of row-col coords
    rprops = regionprops(label_image, img16, coordinates='rc')

    # Extract region areas and eccentricities
    star_area = []
    star_ecc = []
    star_int = []

    for r in rprops:
        star_area.append(r.area)
        star_ecc.append(r.eccentricity)
        star_int.append(r.mean_intensity)

    star_area = np.array(star_area)
    star_ecc = np.array(star_ecc)
    star_int = np.array(star_int)

    int_th = np.percentile(star_int, 50.0)
    area_th = np.percentile(star_area, 95.0)
    ecc_th = np.percentile(star_ecc, 50.0)

    sbar.showMessage('  Intensity threshold : %0.1f' % int_th, 250)
    sbar.showMessage('  Area threshold : %0.1f pixels' % area_th, 250)
    sbar.showMessage('  Eccentricity threshold : %0.1f' % ecc_th, 250)

    # Compile list of good star candidates
    stars = []
    for r in rprops:
        if r.mean_intensity > int_th:
            stars.append(r)

    sbar.showMessage('Good candidates : %d' % len(stars))

    return stars


def estimate_fwhm(img16):
    """
    Estimate mean FWHM of bright sources in image in Fourier space

    Ref
    ----
    R. Mizutani et al., “Estimating the resolution of real images,”
    J. Phys. Conf. Ser., vol. 849, no. 1, p. 012042, Jun. 2017 [Online].
    Available: http://iopscience.iop.org/article/10.1088/1742-6596/849/1/012042/meta. [Accessed: 24-Oct-2018]

    :param img16:
    :return:
    """

    # Magnitude 2D FFT of entire image
    img_k = np.abs(np.fft.fft2(img16))

    # Crop to central region

    # Create



def estimate_background(img16):
    """
    Downsample, median filter and upsample to estimate smooth background
    - catches nebulosity and residual gradients, amp glow, etc

    :param img16: uint16 numpy array, original image
    :return: bg16: uint16 numpy array, estimated background
    """

    from skimage.transform import rescale

    # Isotropic, antialiased downsample by 10
    i_dwn = rescale(img16, )