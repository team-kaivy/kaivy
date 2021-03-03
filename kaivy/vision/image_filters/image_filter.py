########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    This file defines the image filter base class
"""

from zwt.components.component import Component
import numpy as np

class ImageFilter(Component):
    """
    Base class for image filters
    """

    def __init__(self, configuration):
        """
        Initializer
        :param configuration: The filter's configuration
        """
        super().__init__(configuration)
        self.last_processing_time = 0.0  # Time of last processing
        self.disabled = False  # Defines if this filter is currently disabled (and so skipped)

    def reset(self):
        """
        Resets the filter. This function should called when ever a video stream is reset, a video rewinded or skipped
        """
        self.last_processing_time = 0.0

    def process_images(self, images, time_offsets=None, in_place=False, out_data=None):
        """
        Processes the image and returns the result.
        :param images: The source image(s).
        :param time_offsets: The source time offset(s).
        :param in_place Defines if the original image may be modified inplace for performance gains.
        :param out_data: Dictionary to receive detailed information
        :return: The processed image
        """
        return self._process_images_int(images, time_offsets, in_place, out_data) if not self.disabled else images[0]

    def _process_images_int(self, images, time_offsets=None, in_place=False, out_data=None):
        """
        Processes the image and returns the result. Implement custom functionality here.

        :param images: The source image(s).
        :param time_offsets: The source time offset(s).
        :param in_place Defines if the original image may be modified inplace for performance gains.
        :param out_data: Dictionary to receive detailed information
        :return: The processed image
        """
        return images[0]

