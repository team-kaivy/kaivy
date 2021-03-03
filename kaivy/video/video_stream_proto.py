########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    Implements the video streaming prototype class VideoStreamProto
"""

class VideoStreamProto:
    """
    Defines the prototype of a video input source
    """

    def __init__(self):
        """
        Initializer
        """
        self.unique_name = ""
        self.identifier = ""
        self.vendor = "GenericProto"  # The device's vendor name
        self.model = ""  # The device's model name
        self.last_image = None  # A backup of the last returned image data
        self.last_image_time = None  # Defines the time the last image has been captured (time.time)
        self.effective_fps = 0.0  # Effective fps, e.g. if the effective fps is higher than the original fps,
        self.resolution_x = 640  # The camera's horizontal resolution
        self.resolution_y = 480  # The camera's vertical resolution
        self.fps = 60  # Defines the cameras count of frames per second

    def start(self):
        """
        Is called when the device shall be started
        """
        pass

    def pause(self):
        """
        Is called when the device shall be paused
        """
        pass

    def stop(self):
        """
        Is called when the device shall be stopped
        """
        pass

    def rewind(self):
        """
        Is called (if possible) to rewind the video source
        """
        pass

    def available(self):
        """
        Returns if the device is currently available and images can be received
        :return: True if the device is ready
        """
        return True

    def get_resolution(self):
        """
        Returns the stream's resolution (width, height)
        :return: The resolution as width, height
        """
        if self.last_image is not None:
            return self.last_image.shape[1], self.last_image.shape[0]
        else:
            time_stamp, img = self.read_image()
            if img is None:
                return 1, 1
            return img.shape[1], img.shape[0]

    def read_image(self, time_stamp=None, parameters=None):
        """
        Is called when a new image shall be read
        :param time_stamp: The time stamp of the previous update (if available)
        :param parameters: Optional parameters
        :return: (Updated time stamp, New Image) if available. If not (0, None)
        """
        return 0, None

    def on_image_received(self, stream, image):
        """
        Is called when the newest image has been received e.g. from a camera.
        """
        pass

    def handle_post_processing(self, image):
        """
        Applies post-processing effects such as gamma and digital zoom to given input image
        :param image: The input image
        :return: The modified image
        """
        return image

    def handle_raw_image_received(self, image, time_stamp):
        """
        Is called whenever a new raw image is received and returns an optionally preprocessed image
        :param image: The image
        :param time_stamp: The time stamp within the stream
        :return: The new image
        """
        pass

    def get_device_name(self):
        """
        Returns the device's name
        :return: The device name
        """
        if len(self.vendor) and len(self.model):
            return self.vendor+' '+self.model
        elif len(self.vendor):
            return self.vendor
        else:
            return self.model
