########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################


"""
  This file defines a video stream live view screen
"""

from typing import List
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kaivy.video.video_stream_proto import VideoStreamProto
from kaivy.video.video_stream_view import VideoStreamOverlayView
from kaivy.video.video_stream_view import VideoStreamView
from kaivy.common.pan_and_zoom_view import PanAndZoomView


class VideoStreamScreen(Screen):
    """
    This screen type shows up to four video streams separately
    """

    def __init__(self, **kwargs):
        """
        Initializer
        """

        super().__init__(**kwargs)
        self.stream_views: List[VideoStreamView] = []  # The list of views displaying the single video streams
        self.stream_overlay_views = []  # The list of overlay views (in which the stream_views are embedded)
        self.pan_and_zoom_views = []  # The list of pan and zoom views (if available)
        self.stream_list: List[VideoStreamProto] = []  # The connected video streams
        self.video_stream_region = None  # The full region containing the video streams
        self.right_side_view: BoxLayout = None  # Use this view for adding custom controls on the right side
        self.thumbnail_start = -1  # Defines the maximum of full size views. -1 = unlimited
        self.thumbnail_width = 1920 // 6  # Size of a single thumbnail
        self.thumbnail_height = 1080 // 6  # Height of a single thumbnail
        self.thumbnail_stream_count = 0  # Count of thumbnail stream views
        self.use_pan_and_zoom_views = False  # Define if advanced, pannable views shall be used
        self.screen_active = False  # Defines if the screen is currently visible

        self.padding = [0, 0, 0, 0]
        self.size_hint = (1.0, 1.0)

        # Float layout allowing putting thumbnails on to of other streams

        # Create basic screen regions
        screen_region = BoxLayout(orientation='horizontal', size_hint=(1.0, 1.0))
        self.add_widget(screen_region)

        self.video_stream_float_region = FloatLayout(size_hint=(0.7, 1.0))
        self.video_stream_region = BoxLayout(orientation='horizontal', size_hint=(1.0, 1.0),
                                             pos_hint={'center': [0.5, 0.5]})
        self.video_stream_float_region.add_widget(self.video_stream_region)
        self.thumbnail_anchor = AnchorLayout(anchor_x='right', anchor_y='bottom', size_hint=(1.0, 1.0),
                                             pos_hint={'center': [0.5, 0.5]})
        self.thumbnail_region = BoxLayout(orientation='horizontal')
        self.thumbnail_anchor.add_widget(self.thumbnail_region)
        self.video_stream_float_region.add_widget(self.thumbnail_anchor)

        # Prepare right side view - you can add custom controls here
        self.right_side_view = BoxLayout(orientation='vertical', size_hint=(0.0, 0.0))
        self.right_side_view.minimum_width = 0

        # Add stream and rightside views to the main layout
        screen_region.add_widget(self.video_stream_float_region)
        screen_region.add_widget(self.right_side_view)

    def get_stream_views(self) -> List[VideoStreamView]:
        """
        Returns a list of all stream views
        :return: The stream views
        """
        return self.stream_views

    def get_main_stream_view(self) -> VideoStreamView:
        """
        Returns the main stream view
        :return:
        """
        return self.stream_views[0]

    def get_stream_overlay_views(self) -> List[VideoStreamOverlayView]:
        """
        Returns a list of all stream views
        :return: The stream views
        """
        return self.stream_overlay_views

    def get_main_stream_overlay_view(self) -> VideoStreamOverlayView:
        """
        Returns the main stream overlay view
        :return:
        """
        return self.stream_overlay_views[0]

    def select_cameras(self, cameras: List[VideoStreamProto]):
        """
        Defines the cameras which shall be used for the recording session
        :param cameras: An array of cameras
        """
        self.select_streams(cameras)

    def select_streams(self, streams: List[VideoStreamProto]):
        """
        Defines the streams which shall be used for the recording session
        :param streams: An array of VideoStreams
        """
        self.stream_list = streams

        self.stream_views.clear()
        self.stream_overlay_views.clear()
        self.pan_and_zoom_views.clear()

        gridded_stream_count = len(streams)
        self.thumbnail_stream_count = 0

        if self.thumbnail_start != -1:  # If secondary video shall be shown small they don't need to be part of the grid
            if gridded_stream_count >= self.thumbnail_start:
                prev_count = gridded_stream_count
                gridded_stream_count = self.thumbnail_start
                self.thumbnail_stream_count = prev_count - gridded_stream_count

        # Define camera positioning
        if gridded_stream_count >= 4:
            columns = [2, 2]
        elif gridded_stream_count == 3:
            columns = [1, 2]
        elif gridded_stream_count == 2:
            columns = [1, 1]
        else:
            columns = [1]

        # Remove all old views
        self.video_stream_region.clear_widgets()
        self.thumbnail_region.clear_widgets()

        total_index = 0

        # Setup all camera views
        for row_count in columns:  # for all columns
            v_box_layout = BoxLayout(orientation='vertical', size_hint=(1.0, 1.0))
            self.video_stream_region.add_widget(v_box_layout)
            for _ in range(row_count):  # for all rows

                current_stream = streams[total_index] if total_index < len(streams) else None
                if self.use_pan_and_zoom_views:
                    pan_and_zoom_view = \
                        self.handle_create_pan_and_zoom_view(total_index, current_stream)
                    self.pan_and_zoom_views.append(pan_and_zoom_view)
                    cam_view = VideoStreamOverlayView(center=(0.5, 0.5), pos=(0, 0), size_hint=(None, None))
                    pan_and_zoom_view.set_dynamic_widget(cam_view)
                    cam_view.pause()
                    pan_and_zoom_view.add_widget(cam_view)
                    v_box_layout.add_widget(pan_and_zoom_view)
                else:
                    cam_view = self.handle_create_view(total_index, current_stream)
                    cam_view.pause()
                    v_box_layout.add_widget(cam_view)

                self.stream_views.append(cam_view.stream_view)
                self.stream_overlay_views.append(cam_view)

                total_index += 1

        # Setup thumbnails
        self.thumbnail_region.size_hint = (None, None)
        self.thumbnail_region.size = (self.thumbnail_width * self.thumbnail_stream_count, self.thumbnail_height)
        for thumb_index in range(self.thumbnail_stream_count):
            cam_view = VideoStreamOverlayView(size_hint=(None, None),
                                              size=(self.thumbnail_width, self.thumbnail_height))
            cam_view.pause()
            self.thumbnail_region.add_widget(cam_view)
            self.stream_views.append(cam_view.stream_view)
            self.stream_overlay_views.append(cam_view)

        # Connect all streams
        for index, camera in enumerate(self.stream_list):
            if index >= len(self.stream_views):
                break
            self.stream_views[index].select_stream(self.stream_list[index])

    def handle_create_pan_and_zoom_view(self, index, stream) -> PanAndZoomView:
        """
        Handler which is called to create a panning view. May be overwritten to create a customized view.
        :param index: The stream index
        :param stream: The stream which will be assigned to this view
        :return: The view
        """
        return PanAndZoomView(size_hint=(1.0, 1.0))

    def handle_create_view(self, index, stream) -> VideoStreamOverlayView:
        """
        Handler which is called to create an overlay view. May be overwritten to create a customized view.
        :param index: The stream index
        :param stream: The stream which will be assigned to this view
        :return: The view
        """
        return VideoStreamOverlayView(size_hint=(1.0, 1.0))

    def continue_streams(self):
        """
        Continues the video streams
        """
        for view in self.stream_views:
            view.start()

    def pause_streams(self):
        """
        Pauses the video streams
        """
        for view in self.stream_views:
            view.pause()

    def on_enter(self, *args):
        """
        Wake up screen and camera view when screen appears
        :param args: Arguments
        """
        super().on_enter(args)
        self.continue_streams()
        self.screen_active = True

    def on_leave(self, *args):
        """
        Put screen into sleep mode when it disappears
        :param args: Arguments
        """
        super().on_leave(args)
        self.pause_streams()
        self.screen_active = False
