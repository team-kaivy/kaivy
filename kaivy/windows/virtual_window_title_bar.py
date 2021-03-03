########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
    Implements a window title bar view
"""

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, InstructionGroup
import time
from kivymd.uix.button import MDIconButton


class VirtualWindowTitleBar(ButtonBehavior, FloatLayout):
    """
    Display's the title bar of a window
    """

    TITLE_BAR_MIN_WIDTH = 320  # Default title bar width
    TITLE_BAR_HEIGHT = 32  # Default title bar height

    def __init__(self, window):
        super().__init__(size_hint=(1.0, None), size=(40, self.TITLE_BAR_HEIGHT))
        self.window = window
        self.paint_group = InstructionGroup()
        self.canvas.add(self.paint_group)
        self.bind(size=self.update_title)
        self.bind(pos=self.update_title)
        self.text = "title"
        self.title_label = Label(text=self.text, size_hint=(1.0, 1.0))
        self.title_label.pos_hint = {'center': (0.5, 0.5)}
        self.add_widget(self.title_label)
        self.bind(on_release=self.handle_release)
        self.last_tap = 0
        self.double_tap_time = 0.5
        self.button = MDIconButton(icon='arrow-expand', size_hint=(None, None))
        self.add_widget(self.button)
        self.update_title()

    def set_text(self, text):
        """
        Sets a new title text
        :param text:
        :return:
        """
        self.text = text
        self.title_label.text = self.text

    def update_title(self, _=None, __=None):
        """
        Updates the title bar's bounding
        """
        self.paint_group.clear()
        self.paint_group.add(Color(0.5, 0.5, 0.7, 1.0))
        self.paint_group.add(Rectangle(pos=self.pos, size=self.size))
        self.button.pos_hint = {'right': 1.0, 'center_y': 0.5}
        self.button.bind(on_release=self.handle_resize_click)
        self.do_layout()

    def get_required_space(self):
        """
        Returns the minimum required space of the view
        :return: Width, Height tuple
        """
        return (self.TITLE_BAR_MIN_WIDTH, self.TITLE_BAR_HEIGHT)

    def handle_resize_click(self, btn):
        """
        Triggered when the resize button was pressed
        """
        self.window.handle_maximize_restore()

    def handle_release(self, evt):
        """
        Called on click on title bar
        :param evt: The event source
        """
        cur_time = time.time()
        if cur_time - self.last_tap < self.double_tap_time:
            self.window.handle_maximize_restore()
        self.last_tap = cur_time