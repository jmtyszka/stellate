#!/usr/bin/env python3
"""
Adaptive source detection

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

from skimage import transform as tf
from skimage.feature import match_descriptors, ORB, plot_matches
from skimage.color import rgb2gray
from skimage.io import imread
from scipy.misc import imresize
import matplotlib.pyplot as plt

img0 = rgb2gray(imread('saturn.png'))

# Downsample image
img1 = imresize(img0, 0.25)

img2 = tf.rotate(img1, 15)
tform = tf.AffineTransform(scale=(1, 1), rotation=0.5,
                           translation=(-100, -400))
img3 = tf.warp(img1, tform)

descriptor_extractor = ORB(n_keypoints=50)

descriptor_extractor.detect_and_extract(img1)
keypoints1 = descriptor_extractor.keypoints
descriptors1 = descriptor_extractor.descriptors

descriptor_extractor.detect_and_extract(img2)
keypoints2 = descriptor_extractor.keypoints
descriptors2 = descriptor_extractor.descriptors

descriptor_extractor.detect_and_extract(img3)
keypoints3 = descriptor_extractor.keypoints
descriptors3 = descriptor_extractor.descriptors

matches12 = match_descriptors(descriptors1, descriptors2, cross_check=True)
matches13 = match_descriptors(descriptors1, descriptors3, cross_check=True)

fig, ax = plt.subplots(nrows=2, ncols=1)

plt.gray()

plot_matches(ax[0], img1, img2, keypoints1, keypoints2, matches12)
ax[0].axis('off')
ax[0].set_title("Original Image vs. Transformed Image")

plot_matches(ax[1], img1, img3, keypoints1, keypoints3, matches13)
ax[1].axis('off')
ax[1].set_title("Original Image vs. Transformed Image")

plt.show()

"""
Blob detection tests
"""

print('Loading image')
image = imread('saturn.png')
image_gray = rgb2gray(image)

print('Running LOG')
t0 = time.time()
blobs_log = blob_log(image_gray, max_sigma=30, num_sigma=10, threshold=.1)
blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)
t_log = time.time() - t0

print('Running DOG')
t0 = time.time()
blobs_dog = blob_dog(image_gray, max_sigma=30, threshold=.1)
blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2)
t_dog = time.time() - t0

print('Running DOH')
t0 = time.time()
blobs_doh = blob_doh(image_gray, max_sigma=30, threshold=.01)
t_doh = time.time() - t0

print('LOG : %0.3f s' % t_log)
print('DOG : %0.3f s' % t_dog)
print('DOH : %0.3f s' % t_doh)

print('Constructing figure')

blobs_list = [blobs_log, blobs_dog, blobs_doh]
colors = ['yellow', 'lime', 'red']
titles = ['Laplacian of Gaussian', 'Difference of Gaussian',
          'Determinant of Hessian']
sequence = zip(blobs_list, colors, titles)

fig, axes = plt.subplots(1, 3, figsize=(9, 3), sharex=True, sharey=True,
                         subplot_kw={'adjustable': 'box-forced'})
ax = axes.ravel()

for idx, (blobs, color, title) in enumerate(sequence):
    ax[idx].set_title(title)
    ax[idx].imshow(image, interpolation='nearest')
    for blob in blobs:
        y, x, r = blob
        c = plt.Circle((x, y), r, color=color, linewidth=2, fill=False)
        ax[idx].add_patch(c)
    ax[idx].set_axis_off()

plt.tight_layout()
plt.show()