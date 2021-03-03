########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

from kivy.uix.boxlayout import BoxLayout
from kivy.event import EventDispatcher
from kivy.uix.stencilview import StencilView
from kivy.properties import StringProperty, ListProperty, VariableListProperty
from kaivy.windows.virtual_window_title_bar import VirtualWindowTitleBar


class VirtualWindow(BoxLayout, StencilView):
    """
    Defines a virtual window which can be placed in a floating layout, moved within it and arranged with other windows

    Events:
    on_content_appeared - Called when the window's content became visible
    on_content_disappeared - Called when the window's content became invisible
    """

    STATE_NORMAL = 0  # Normally displayed
    STATE_MINIMIZED = 1  # Window is minimized
    STATE_MAXIMIZED = 2  # Window is maximized

    ANCHOR_LEFT = 1  # Size and position relative to top
    ANCHOR_RIGHT = 2  # Size and position relative to right
    ANCHOR_TOP = 3  # Size and position relative to top
    ANCHOR_BOTTOM = 4  # Size and position relative to bottom

    window_title = StringProperty("windowTitle")  # The window's title
    window_pos = ListProperty((0, 0))  # The position
    window_anchors = VariableListProperty((ANCHOR_LEFT, ANCHOR_TOP))  # The view's anchors

    def __init__(self, window_manager: 'VirtualWindowManager', client_widget):
        """
        Initializer
        :param window_manager: The window manager
        """
        super().__init__()
        self.window_state = self.STATE_NORMAL
        self.orientation = 'vertical'
        self.title_bar = VirtualWindowTitleBar(self)
        self.add_widget(self.title_bar)
        self.window_manager = window_manager
        self.client_widget = client_widget
        client_widget.size_hint = (1.0, 1.0)
        self.client_widget.parent_window = self  # Assign self as parent window of widget
        self.add_widget(client_widget)
        self.visible = False
        self.center = (0.0, 0.0)
        self.size_hint = (None, None)
        self.pos = (0, 0)
        self.optimal_size = (100, 100)
        self.anchors = set()
        self.content_recently_visible = False  # State variable if the content was recently visible
        try:
            opt_size = self.get_optimal_size()
            self.size = opt_size
        except NameError:
            pass
        fbind = self.fbind
        fbind('window_title', self.handle_title_update)
        fbind("window_pos", self.handle_pos_update)
        self.register_event_type("on_content_appeared")
        self.register_event_type("on_content_disappeared")
        self.adjust_position()
        self.client_widget.bind(size=self.handle_client_widget_resized)

    def get_optimal_size(self):
        if self.window_state == self.STATE_MINIMIZED:
            required_size = self.title_bar.get_required_space()
            self.optimal_size = required_size
            return self.optimal_size

        self.optimal_size = self.client_widget.get_optimal_size()
        required_height = self.optimal_size[1] + self.title_bar.get_required_space()[1]
        self.optimal_size = (self.optimal_size[0], required_height)
        return self.optimal_size

    def show(self, state=STATE_NORMAL):
        """
        Shows this window

        :param state: The initial state
        """
        if not self.visible:
            self.visible = True
            self.window_manager.show_window(self)
            if state == self.STATE_MINIMIZED:
                self.minimize()
        self.handle_visibility_change()

    def hide(self):
        """
        Hides this window
        :return:
        """
        if self.visible:
            self.visible = False
            self.window_manager.hide_window(self)
        self.handle_visibility_change()

    def get_content_visible(self):
        """
        Returns if the content is currently displayed
        :return: True if the content is visible
        """
        return self.visible and self.window_state != self.STATE_MINIMIZED

    def minimize(self):
        """
        Minimizes the window
        """
        if self.window_state == self.STATE_MINIMIZED:
            return

        self.window_state = self.STATE_MINIMIZED
        self.client_widget.size_hint_y = 0.0
        opt_size = self.get_optimal_size()
        self.size = opt_size
        self.remove_widget(self.client_widget)
        self.adjust_position()
        self.handle_visibility_change()

    def restore(self):
        """
        Restores the window
        """
        if self.window_state==self.STATE_NORMAL:
            return
        self.window_state = self.STATE_NORMAL
        self.client_widget.size_hint_y = None
        opt_size = self.get_optimal_size()
        self.size = opt_size
        self.add_widget(self.client_widget)
        self.adjust_position()
        self.handle_visibility_change()

    def handle_maximize_restore(self):
        """
        Handles the maximizing and storing of the window
        :return:
        """
        if self.window_state != self.STATE_MINIMIZED:
            self.minimize()
        else:
            self.restore()

    def handle_visibility_change(self):
        """
        Verifies if the window recently visually appeared or disappeared
        :return:
        """
        cur_visible = self.get_content_visible()
        if cur_visible and not self.content_recently_visible:
            self.content_recently_visible = True
            self.dispatch("on_content_appeared")
        elif not cur_visible and self.content_recently_visible:
            self.content_recently_visible = False
            self.dispatch("on_content_disappeared")

    def handle_client_widget_resized(self, view, size):
        """
        Called when the client widget was resized
        :param view: The view
        :param size: The new size
        """
        self.optimal_size = opt_size = self.get_optimal_size()
        self.size = opt_size
        self.adjust_position()

    def on_content_appeared(self):
        """
        Called when the content appeared (after it was previously invisible)
        :return:
        """
        pass

    def on_content_disappeared(self):
        """
        Called when the content disappeared (after it was previously visible)
        """
        pass

    def adjust_position(self):
        """
        Adjusts position using the current size and given window position
        :return:
        """
        if self.ANCHOR_TOP in self.window_anchors:
            desk_size = self.window_manager.get_desktop_size()
            x_pos = self.window_pos[0]
            y_pos = desk_size[1] - self.window_pos[1] - self.size[1]
            self.pos = (x_pos, y_pos)

    def handle_title_update(self, view, value):
        """
        Called upon title text change
        """
        if self.title_bar is not None:
            self.title_bar.set_text(self.window_title)

    def handle_desktop_resized(self, last_size, new_size):
        """
        Called when the desktop resized
        :param last_size: The last size
        :param new_size: The new size
        """
        self.adjust_position()

    def handle_pos_update(self, view, value):
        """
        Called when the position changed
        :param view: Self
        :param value: The new value
        """
        self.adjust_position()


class VirtualWindowRootView:
    """
    Base class for a view which shall be stored as root view within a window. Should always be paired with a Kivy
    view base class.
    """

    def __init__(self):
        """
        Initializer
        """
        self.parent_window = None  # The parent window once it's attached to one

    def get_optimal_size(self):
        """
        Returns the optimum view size in pixels
        :return: The size in pixels as tuple
        """
        return 100, 100

    def auto_size(self):
        """
        Auto sizes the current view
        """
        self.size = self.get_optimal_size()
