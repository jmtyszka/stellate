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


def starfinder(img16):
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
    print('  Noise sd : %0.3f' % sd_n)
    print('  Thresholding at %0.3f' % th)

    # Create superthreshold mask
    mask = img16 > th

    # Remove objects < 9 pixels in size
    print('  Removing small objects')
    mask_clean = remove_small_objects(mask, min_size=9)

    # Label connected regions
    print('  Labeling connected regions')
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

    print('  Intensity threshold : %0.1f' % int_th)
    print('  Area threshold : %0.1f pixels' % area_th)
    print('  Eccentricity threshold : %0.1f' % ecc_th)

    # Compile list of good star candidates
    stars = []
    for r in rprops:
        if r.mean_intensity > int_th:
            stars.append(r)

    print('  Found %d potential stars' % len(rprops))
    print('  Identified %d good star candidates' % (len(stars)))

    return stars



