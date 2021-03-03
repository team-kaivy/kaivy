########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    This file defines the resize filter which can resize images and transform them into a standardized format
"""

from .image_filter import ImageFilter
import numpy as np
import cv2


class ResizeImageFilter(ImageFilter):
    """
    The resize filter resizes and image to the desired dimensions
    """

    def __init__(self, configuration):
        """
        Initializer
        :param configuration: The configuration dictionary
        """
        super().__init__(configuration)

        self.target_width_pixels = None  # Defines the target width in pixels
        self.target_height_pixels = None  # Defines the target height in pixels
        self.target_width_percent = None  # Defines the target width in percent. Pixel size has a higher priority.
        self.target_height_percent = None  # Defines the target height in percent. Pixel size has a higher priority.
        self.crop = True  # Defines the image may be cropped if required
        self.keep_aspect = True  # Defines if the aspect ratio shall be kept
        self.bicubic = False  # Bicubic rescaling?
        # If the image shall not be cropped this color is used to fill the missing gaps
        self.fill_color = np.array([0, 0, 0], dtype=np.uint8)

    def _process_images_int(self, images, time_offsets=None, in_place=False, out_data=None):
        """
        Processes the image and returns the result.
        :param images: The source image(s).
        :param time_offsets: The source time offset(s).
        :param in_place Defines if the original image may be modified inplace for performance gains.
        :param out_data: Dictionary to receive detailed information
        :return: The processed image
        """

        # try to use desired target size in pixels by default
        tar_width = self.target_width_pixels
        tar_height = self.target_height_pixels

        src_image = images[0]

        # if target size not defined yet but a percentage value use this instead
        if tar_width is None and self.target_width_percent is not None:
            tar_width = round(src_image.shape[1] * self.target_width_percent)
        if tar_height is None and self.target_height_percent is not None:
            tar_height = round(src_image.shape[0] * self.target_height_percent)

        # if still a value is missing use original width or height
        if tar_width is None:
            tar_width = round(src_image.shape[1] * (tar_height / src_image.shape[0]))
        if tar_height is None:
            tar_height = round(src_image.shape[0] * (tar_width / src_image.shape[1]))

        keep_aspect = self.keep_aspect

        new_width = tar_width
        new_height = tar_height

        x_scaling = new_width / src_image.shape[1]
        y_scaling = new_height / src_image.shape[0]

        if keep_aspect:
            if self.crop:  # Minimize as less as possible or maximize as much as possible, rest will be cropped
                x_scaling = y_scaling = x_scaling if x_scaling > y_scaling else y_scaling
            else:  # Minimize as much as possible so there will be not overlap, rest will be filled
                x_scaling = y_scaling = y_scaling if x_scaling > y_scaling else x_scaling

        tar_resizing = (round(x_scaling * src_image.shape[1]), round(y_scaling * src_image.shape[0]))

        if self.keep_aspect and not self.crop:
            tar_resizing = (tar_width, tar_height)

        resized_image = cv2.resize(src_image,
                                   tar_resizing, interpolation=(cv2.INTER_CUBIC if self.bicubic else cv2.INTER_LINEAR))

        if not keep_aspect:
            return resized_image

        if self.crop:  # Crop out relevant region from big image
            cw = resized_image.shape[1]  # full width
            hw = cw // 2  # half width
            thw = tar_width // 2  # half target width
            twe = tar_width % 2  # uneven rest of target with
            ch = resized_image.shape[0]  # full height
            hh = ch // 2  # half height
            thh = tar_height // 2  # half target height
            the = tar_height % 2  # uneven rest of target height
            if len(resized_image.shape) == 3:
                resized_image = resized_image[hh - thh:hh + thh + the, hw - thw:hw + thw + twe, :]
            else:
                resized_image = resized_image[hh - thh:hh + thh + the, hw - thw:hw + thw + twe]
        else:
            if len(src_image.shape) == 3:
                new_image = np.zeros((tar_height, tar_width, src_image.shape[2]), self.fill_color.dtype)
            else:
                new_image = np.zeros((tar_height, tar_width), self.fill_color.dtype)
            new_image[:, :] = self.fill_color
            cw = resized_image.shape[1]
            hw = cw // 2
            thw = tar_width // 2
            twe = tar_width % 2  # uneven rest of target with
            ch = resized_image.shape[0]
            hh = ch // 2
            thh = tar_height // 2
            the = tar_height % 2  # uneven rest of target height
            if len(src_image.shape) == 3:
                new_image[thh - hh:thh + hh + the, thw - hw:thw + hw + twe, :] = resized_image
            else:
                new_image[thh - hh:thh + hh + the, thw - hw:thw + hw + twe] = resized_image
            resized_image = new_image

        return resized_image
