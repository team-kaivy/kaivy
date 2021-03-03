########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    This file defines the BlendImageFilter class which blends one image above another
"""

from .image_filter import ImageFilter
import numpy as np
import cv2


class BlendImageFilter(ImageFilter):
    """
    The dual image mix filter allows the blending of one image onto another one
    """

    def __init__(self, configuration):
        """
        Initializer
        :param configuration: The configuration dictionary
        """
        super().__init__(configuration)

    def _process_images_int(self, images, time_offsets=None, in_place=False, out_data=None):
        """
        Processes the image and returns the result. The first image is assumed to hold the alpha mask
        :param images: The source image(s).
        :param time_offsets: The source time offset(s).
        :param in_place Defines if the original image may be modified inplace for performance gains.
        :param out_data: Dictionary to receive detailed information
        :return: The processed image
        """

        if len(images) != 2:
            raise ValueError("DualImage filter requires an image count of two")

        if images[0].shape[0] != images[1].shape[0] or images[0].shape[1] != images[1].shape[1]:
            raise ValueError("Image sizes have to match")

        if images[0].shape[2] == 3:  # If front image is fully solid we can return it directly
            return np.copy(images[0])

        # Convert uint8 to float
        image_zero_float = images[0].astype(float)
        foreground = image_zero_float[:, :, 0:3]
        background = images[1].astype(float)

        # Normalize the alpha mask to keep intensity between 0 and 1
        alpha = image_zero_float[:, :, 3] / 255
        alpha = np.stack([alpha, alpha, alpha], axis=2)

        # Multiply the foreground with the alpha matte
        foreground = cv2.multiply(alpha, foreground)

        # Multiply the background with ( 1 - alpha )
        background = cv2.multiply(1.0 - alpha, background)

        # Add the masked foreground and background.
        result = cv2.add(foreground, background).astype(np.uint8)

        return result  # Return interpolated image
