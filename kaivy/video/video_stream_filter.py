########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

"""
  This file defines VideoStreamFilter - the base for post processing video streams
"""

import time
from kaivy.video.video_stream_proto import VideoStreamProto


class VideoStreamFilter(VideoStreamProto):
    """
    The video stream filter class can apply effects to a video stream. If you no filters are added or applied it can
    act as pass through component.
    """

    def __init__(self, sources):
        """
        Initializer the stream
        :param sources: The source list
        :param configuration:
        """
        super().__init__()
        self.on_image_update_callback = None  # Is called when ever the image is modified. Provides the image, receives a
        # modified one. Parameters: filter, image -> image
        self.sources = []
        self.last_image_times = []
        self.last_images = []
        self.images_received = [None for _ in self.sources]
        self.images_received_count = 0
        self.still_image_filters = []
        self.set_sources(sources)

    def set_sources(self, sources):
        """
        Sets the new source list
        :param sources: The new source list
        """
        self.sources = sources
        self.last_image_times = [0.0 for _ in self.sources]
        self.last_images = [None for _ in self.sources]

    def set_still_image_filter(self, new_filter):
        """
        Sets given filter as new (and only) still image filter
        :param new_filter: The filter
        """
        self.still_image_filters = [new_filter]

    def add_still_image_filter(self, new_filter):
        """
        Add given filter
        :param new_filter: The filter
        """
        self.still_image_filters.append(new_filter)

    def read_image(self, time_stamp=None, parameters=None):
        modified = False
        for index, cur_source in enumerate(self.sources):
            stamp, image = cur_source.read_image(time_stamp, parameters)
            if image is None:
                continue
            if stamp != self.last_image_times[index]:
                modified = True
                self.last_images[index] = image
                self.last_image_times[index] = stamp
        if modified:
            self.last_image_time = time.time()
            self.last_image = self.apply_filter()
            if self.on_image_update_callback is not None:
                self.last_image = self.on_image_update_callback(self, self.last_image)
        return self.last_image_time, self.last_image

    def apply_filter(self):
        """
        Apply filter to the newest image received
        :return: The mixed image to return
        """
        image = self.last_images[0]
        for cur_filter in self.still_image_filters:
            image = cur_filter.process_images([image])
        return image

    def trigger_image_capturing(self, session):
        """
        Trigger the image capturing process by the camera or source. Override this function for real cameras and
        when the image was received call the on_image_received method.
        """
        self.images_received = [None for _ in self.sources]
        self.images_received_count = 0
        for source in self.sources:  # forward commands
            source.trigger_image_capturing()

    def available(self):
        """
        Returns if the camera is available.
        :return: True if the camera is ready
        """
        available = True
        for source in self.sources:  # forward commands
            available = available and source.available()

        return available

    def on_image_received(self, stream, image):
        """
        Is called when the newest image has been received.
        :return:
        """
        for index, source in enumerate(self.sources):  # forward commands
            if stream == source:
                self.images_received[index] = image
                self.images_received += 1
                if self.images_received == len(self.sources):
                    super.on_image_received(self.read_image())

    def start(self):
        """
        Is called to continue the stream
        """
        for source in self.sources:  # forward commands
            source.start()

    def stop(self):
        """
        Is called to stop the stream
        :return:
        """
        self.last_image_time = 0.0
        for source in self.sources:  # forward commands
            source.stop()

    def pause(self):
        """
        Is called to pause the stream
        :return:
        """
        for source in self.sources:  # forward commands
            source.pause()

    def rewind(self):
        """
        Rewinds this stream (if possible)
        """
        self.last_image_time = 0.0
        for source in self.sources:  # forward commands
            source.rewind()
