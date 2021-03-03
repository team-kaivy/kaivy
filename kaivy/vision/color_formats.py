########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

import cv2


class ColorFormatConverter:
    """
    Color format conversion helper class
    """
    G8 = 0  # Grayscale 8-Bit
    RGB = 1  # 24 bit RGB
    BGR = 2  # 24 bit BGR
    RGBA = 3  # 32 bit RGBA
    BGRA = 4  # 32 bit BGRA

    # Conversion tables
    # From single channel to other format
    IL1 = {G8: None, RGB: cv2.COLOR_GRAY2RGB, BGR: cv2.COLOR_GRAY2BGR, RGBA: cv2.COLOR_GRAY2RGBA,
           BGRA: cv2.COLOR_GRAY2BGRA}
    # 3 channels RGB order
    IL3_RGB = {G8: cv2.COLOR_RGB2GRAY, RGB: None, BGR: cv2.COLOR_RGB2BGR, RGBA: cv2.COLOR_RGB2RGBA,
               BGRA: cv2.COLOR_RGB2BGRA}
    # 3 channels BGR order
    IL3_BGR = {G8: cv2.COLOR_BGR2GRAY, RGB: cv2.COLOR_BGR2RGB, BGR: None, RGBA: cv2.COLOR_BGR2RGBA,
               BGRA: cv2.COLOR_BGR2BGRA}
    # 4 channels RGBA order
    IL4_RGBA = {G8: cv2.COLOR_RGBA2GRAY, RGB: cv2.COLOR_RGBA2RGB, BGR: cv2.COLOR_RGBA2BGR, RGBA: None,
                BGRA: cv2.COLOR_RGBA2BGRA}
    # 4 channels BGRA order
    IL4_BGRA = {G8: cv2.COLOR_BGRA2GRAY, RGB: cv2.COLOR_BGRA2RGB, BGR: cv2.COLOR_BGRA2BGR, RGBA: cv2.COLOR_BGRA2RGBA,
                BGRA: None}

    @classmethod
    def ensure_format_cv(cls, input_image, output_format, bgr_order=True):
        """
        Guarantees the output_format provided as outcome for given input if the image is convertible
        :param input_image: The input image
        :param output_format: The desired output format
        :param bgr_order: Defines if BGR order shall be assumed (the image does not contain this information)
        :return: The converted image
        """
        conversion_dict = None
        # find conversion method in table
        input_channels = 1 if len(input_image.shape) == 2 else input_image.shape[2]
        if input_channels == 1:
            conversion_dict = cls.IL1
        elif input_channels == 3:
            conversion_dict = cls.IL3_BGR if bgr_order else cls.IL3_RGB
        elif input_channels == 4:
            conversion_dict = cls.IL3_BGRA if bgr_order else cls.IL3_RGBA
        if conversion_dict is None or output_format not in conversion_dict:
            raise ValueError()
        # convert image
        conversion_method = conversion_dict[output_format]
        return cv2.cvtColor(input_image, conversion_method) if conversion_method is not None else input_image
