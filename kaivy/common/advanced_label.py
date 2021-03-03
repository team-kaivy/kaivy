########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior


class AdvancedLabel(ButtonBehavior, Label):
    """
    The advanced label class adds some comfort to the base class such as automatic size adaption when the text changed
    """

    def __init__(self, **kwargs):
        super(AdvancedLabel, self).__init__(**kwargs)
        self.border = (0, 0)  # Defines the amount of space to add to the texture size
        self.auto_size = False  # Defines if the label shall automatically adapt to the texture's size
        self.bind(texture_size=self.texture_size_changed)

    def update_auto_size(self, new_size):
        """
        Updates the size given new texture size
        :param new_size: The new texture size
        """
        self.size = (self.border[0] + new_size[0], self.border[1] + new_size[1])

    def refresh(self):
        """
        Enforce instant texture size update outside
        """
        self._label.refresh()
        self.update_auto_size(self._label.content_size)

    def texture_size_changed(self, component, value):
        """
        Is called when the texture size changed
        :param component: The label
        :param value: The new size
        """
        if self.auto_size:
            self.update_auto_size(new_size=value)
