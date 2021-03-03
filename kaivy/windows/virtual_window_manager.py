########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################


from kivy.uix.floatlayout import FloatLayout


class VirtualWindowManager:
    """
    Manages a set of windows in a floating layout
    """

    def __init__(self, floating_area: FloatLayout):
        """
        Initializer
        :param floating_area: The area where the windows are shown
        """
        self.floating_area: FloatLayout = floating_area
        self.visible_windows = []
        self.last_size = list(self.floating_area.size)
        self.floating_area.bind(size=self.handle_area_resized)

    def show_window(self, window):
        """
        Shows given window
        :param window: The window of type VirtualWindow to show
        :return:
        """
        if window not in self.visible_windows:
            self.floating_area.add_widget(window)
            self.visible_windows.append(window)

    def hide_window(self, window):
        """
        Hides given window
        :param window: The window of type VirtualWindow to hide
        :return:
        """
        if window in self.visible_windows:
            self.floating_area.remove_widget(window)
            self.visible_windows.remove(window)

    def get_desktop_size(self):
        """
        Returns the desktop's size
        :return:
        """
        return self.floating_area.size

    def handle_area_resized(self, view, new_size):
        """
        Called when the area resized
        :param view: The updated view
        :param new_size: The new size
        :return:
        """
        for cur_window in self.visible_windows:  # Notify all windows about the resizing
            cur_window.handle_desktop_resized(self.last_size, list(new_size))
