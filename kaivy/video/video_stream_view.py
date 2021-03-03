########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################


import time
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.uix.floatlayout import FloatLayout
from kaivy.common.advanced_image import AdvancedImage
from kaivy.video.video_stream_proto import VideoStreamProto


class VideoStreamView(AdvancedImage, EventDispatcher):
    """
    The VideoStreamView displays a VideoStream from an arbitrary source.

    Events:
        on_image_data_changed(new_image) - Called upon each image update
    """

    def __init__(self, **kwargs):
        """
        Initializer
        :param kwargs:
        """
        super().__init__(**kwargs)

        self.device: VideoStreamProto = None  # The camera to be used
        self.fps: int = 60  # The frame rate at which the video shall be played
        self.max_fps = 60  # Defines the maxiumum frequency with which the view is updated. May be reduced to save
        # energy. The effective fps is though defined in fps.
        self.last_time_stamp: float = None  # The time stamp of the last image received
        self.timer = None  # The automatic image update timer to fetch the next frame
        self.image_texture = None  # The last image received
        self.allow_stretch = True  # Scale the image to the view's full area
        self.register_event_type('on_image_data_changed')
        # Sender and Image, has to return Image (and may manipulate it)

        self.start()  # Start stream by default

    def get_stream_view(self):
        """
        Returns the stream view
        :return:
        """
        return self

    def get_original_image_size(self):
        """
        Returns the original image size in pixels
        :return: The original image's size as tuple
        """
        return self.texture_size

    def select_camera(self, device):
        """
        Selects a new camera device
        :param device: The new device type
        """
        self.device = device

    def select_stream(self, stream):
        """
        Selects a new video stream
        :param stream: The new stream
        """
        self.device = stream

    def start(self):
        """
        Starts the image capturing of the camera device
        """
        if self.timer is None:
            self.timer = Clock.schedule_interval(self.update, 1.0 / self.max_fps)

        if self.device is not None:
            self.device.start()

    def set_fps(self, new_fps):
        """
        Sets a new fps limit for this view
        :param new_fps: The new fps limit
        """
        self.fps = new_fps
        if self.timer is not None:
            self.timer.cancel()
        if self.fps!=0.0:
            self.timer = Clock.schedule_interval(self.update, 1.0 / self.fps)

    def pause(self):
        """
        Pauses the image capturing
        """
        if self.timer is not None:
            Clock.unschedule(self.timer)
            self.timer = None

        if self.device is not None:
            self.device.pause()

    def stop(self):
        """
        Rewinds this stream (if possible)
        """
        self.pause()
        self.device.stop()

    def rewind(self):
        """
        Rewinds this stream (if possible)
        """
        if self.device is not None:
            self.device.rewind()

    def update(self, dt):
        """
        Updates the preview image in a defined interval
        :param dt: The component
        :return:
        """
        if self.device is not None and self.device.available():  # Camera attached and available ?
            if self.last_time_stamp is not None and not time.time() > self.last_time_stamp + 1.0 / self.fps:  # if too few time spent since last time stamp skip
                return
            stamp, frame = self.device.read_image(time_stamp=self.last_time_stamp)
            if frame is None or stamp == self.last_time_stamp:  # continue if nothing was updated
                return
            self.last_time_stamp = stamp  # Remember last time stamp to prevent highspeed-nothing
            if len(self.get_property_observers(
                    'on_image_data_changed')) > 0:  # If a handler is set, call it when ever the image data changed
                frame = self.dispatch('on_image_data_changed', frame)
            self.set_image_data(frame)

    def on_image_data_changed(self, image):
        """
        Called when ever the image was updated
        :param image: The original image
        :return: The modified image
        """
        return image


class VideoStreamOverlayView(FloatLayout):
    """
    The VideoStreamOverlayView enhances the VideoStreamOverlay by an overlay region in which elements such as buttons
    may be placed.
    """

    def __init__(self, **kwargs):
        """
        Initializer
        :param kwargs:
        """
        super().__init__(**kwargs)

        self.stream_view = VideoStreamView(size_hint=(1.0, 1.0), pos_hint={'center': [0.5, 0.5]})
        self.add_widget(self.stream_view)

        self.start()

    def get_stream_view(self):
        """
        Returns the stream view
        :return:
        """
        return self.stream_view

    def get_original_image_size(self):
        """
        Returns the original image size in pixels
        :return: The original image's size as tuple
        """
        return self.stream_view.get_original_image_size()

    def select_camera(self, device):
        """
        Selects a new camera device
        :param device: The new device type
        :return: The new device type
        """
        self.stream_view.select_camera(device)

    def select_stream(self, stream):
        """
        Selects a new video stream
        :param stream: The new stream
        """
        self.stream_view.select_stream(stream)

    def start(self):
        """
        Starts the image capturing of the camera device
        """
        self.stream_view.start()

    def pause(self):
        """
        Pauses the image capturing
        """
        self.stream_view.pause()

    def update(self, dt):
        """
        Updates the preview image in a defined interval
        :param dt: The component
        :return:
        """
        self.stream_view.update()

    def stop(self):
        """
        Rewinds this stream (if possible)
        """
        self.stream_view.stop()

    def rewind(self):
        """
        Rewinds this stream (if possible)
        """
        self.stream_view.rewind()
