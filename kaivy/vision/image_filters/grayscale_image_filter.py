########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    This file defines the grayscale image filter
"""

from .image_filter import ImageFilter
import numpy as np
import cv2
import copy

class GrayscaleFilter(ImageFilter):
    """
    The filter converts an image to grayscale
    """

    def __init__(self, configuration):
        """
        Initializer
        :param configuration: The configuration dictionary
        """
        super().__init__(configuration)

    def _process_images_int(self, images, time_offsets=None, in_place=False, out_data=None):
        """
        Processes the image and returns the result.
        :param images: The source image(s).
        :param time_offsets: The source time offset(s).
        :param in_place Defines if the original image may be modified inplace for performance gains.
        :param out_data: Dictionary to receive detailed information
        :return: The processed image
        """

        src_image = copy.deepcopy(images[0])

        if len(src_image.shape)==2:
            return src_image

        if len(src_image.shape)==4:
            return cv2.cvtColor(cv2.cvtColor(src_image, cv2.COLOR_BGRA2GRAY), cv2.COLOR_GRAY2BGRA)
        else:
            return cv2.cvtColor(cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)