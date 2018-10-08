#!/usr/bin/env python3
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