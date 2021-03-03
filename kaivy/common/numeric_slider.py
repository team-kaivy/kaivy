########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
Implements the numeric slider class which combines a slider with a label to show it's current value
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label


class NumericSlider(BoxLayout):
    """
    Defines a slider control which displays a label, a slider and optionally a text field to modify a property
    """

    def __init__(self, name, value, minimum, maximum, step_size=1, user_data=None):
        """
        Initializes the slider
        :param name: The slider's name
        :param value: The slider's default value
        :param minimum: The minimum value
        :param maximum: The maximum value
        :param step_size: The step granularity
        :param user_data: The user data (e.g. the property)
        """
        if isinstance(minimum, bool):
            minimum = int(minimum)
            maximum = int(maximum)
            value = int(value)
            step_size = 1
            self.is_boolean = True
        else:
            self.is_boolean = False
        super().__init__()
        self.orientation = 'vertical'
        self.value_name = name  # The property's name / label
        self.minimum_val = minimum  # The minimum value
        self.maximum_val = maximum  # The maximum value
        self.user_data = user_data  # The user data
        self.setter = None  # Setter method
        self.size_hint = (1.0, None)
        self.height = 80
        # Add label
        label = Label(text=name, size_hint=(1.0, None), font_size='20sp')
        label.height = 25
        self.add_widget(label)
        # Add slider
        self.slider = Slider(min=self.minimum_val, max=self.maximum_val, value=value)
        self.slider.size_hint = (1.0, None)
        self.slider.height = 60
        self.slider.step = step_size
        self.add_widget(self.slider)
        self.slider.bind(on_touch_move=self.slider_moved)
        self.slider.bind(on_touch_down=self.slider_touch_down)
        self.slider.bind(on_touch_up=self.slider_touch_up)
        self.touched = False  # Currently touched?

    def get_value(self):
        """
        Returns the current value
        :return: The value
        """
        return bool(self.slider.value) if self.is_boolean else int(self.slider.value) \
            if isinstance(self.maximum_val,int) else self.slider.value

    def set_value(self, value):
        """
        Sets a new  value
        :return: The new value
        """
        self.slider.value = int(value) if self.is_boolean else value

    def slider_moved(self, slider, value):
        """
        Is called when ever the slider is moved
        :param slider: The slider
        """
        if not self.touched:
            return False

        if self.setter is not None:
            self.setter(self, self.user_data, bool(slider.value) if self.is_boolean else slider.value)

    def slider_touch_down(self, slider, pos):
        """
        Is called when ever the slider is touched
        :param slider: The slider
        :param pos: The touch pos
        """
        if not self.collide_point(*pos.pos):
            return
        self.touched = True

    def slider_touch_up(self, slider, pos):
        """
        Is called when ever the slider touch was released
        :param slider: The slider
        :param pos: The current movement pos
        """
        if not self.collide_point(*pos.pos) or not self.touched:
            self.touched = False
            return

        self.touched = False

        if self.setter is not None:
            self.setter(self, self.user_data, bool(slider.value) if self.is_boolean else slider.value)

    def property_modified_callback(self, property_object, value):
        """
        Can be set as callback in the property's callback list
        :param property_object: The property which triggered the event
        :param value: The new value assigned
        """
        if property_object is self.user_data:
            if self.slider.value != value:
                if self.is_boolean:
                    self.slider.value = int(value)
                else:
                    self.slider.value = value
