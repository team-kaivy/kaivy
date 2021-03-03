########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    This file defines the PassThrough filter which ... passes the image 1:1, amazing, isn't it?
"""

from .image_filter import ImageFilter
import numpy as np
import cv2


class PassthroughImageFilter(ImageFilter):
    """
    The passthrough filter returns the provided image. It servers as placeholder if no filter shall be applied
    """

    def __init__(self, configuration):
        """
        Initializer
        :param configuration: The configuration dictionary
        """
        super().__init__(configuration)
        self.on_apply_filter = None  # Is called as filter. Passes the object and the image list, awaits an image

    def _process_images_int(self, images, time_offsets=None, in_place=False, out_data=None):
        """
        Processes the image and returns the result.
        :param images: The source image(s).
        :param time_offsets: The source time offset(s).
        :param in_place Defines if the original image may be modified inplace for performance gains.
        :param out_data: Dictionary to receive detailed information
        :return: The processed image
        """

        if self.on_apply_filter is not None:
            return self.on_apply_filter(images[0])

        return np.copy(images[0])