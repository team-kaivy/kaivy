########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from .advanced_label import AdvancedLabel


class LabeledCheckbox(BoxLayout):
    """
    The labeled checkbox widget combines a checkbox component which in Kivy just consists of the box itself and
    a clickable label which also toggles the checkbox state to mimic a classic checkbox components from other UI
    systems.
    """

    def __init__(self, **kwargs):
        """
        Initializer
        :param kwargs:
        """
        super().__init__(**kwargs)

        self.on_checkbox_state = None  # Is called with this object and the new state (bool) when the state changed

        self.orientation = 'horizontal'
        self.checkbox: CheckBox = CheckBox(size_hint=(None, None), size=('30dp', '30dp'))
        self.add_widget(self.checkbox)
        self.text_label: AdvancedLabel = AdvancedLabel(text="", size_hint=(None, None))
        self.text_label.auto_size = True
        self.text_label.border = (5, 12)
        self.add_widget(self.text_label)
        self.text_label.bind(on_release=self._label_clicked)
        self.bind(disabled=self._set_disabled)

        self.checkbox.bind(state=self._state_change)

    def get_checkbox(self):
        """
        Returns the checkbox component
        :return:
        """
        return self.checkbox

    def get_label(self):
        """
        Returns the label component for customization
        :return:
        """
        return self.text_label

    def set_text(self, text):
        """
        Assigns a new label text
        :param text: The new text
        """
        self.text_label.text = text
        self.text_label.refresh()
        self.do_layout()
        self.size = self.minimum_size

    def _state_change(self, component, value):
        """
        Is called when ever the checkbox's state changed
        :param value: The new value
        """
        if self.on_checkbox_state:
            self.on_checkbox_state(self, True if value == 'down' else False)

    def _set_disabled(self, component, value):
        """
        Called when the disabled property was modified. Forwards the state to the sub components
        :param component: The component
        :param value: The new value
        """
        self.text_label.disabled = value
        self.checkbox.disabled = value

    def _label_clicked(self, component):
        """
        Is called when the label is clicked. Forwards the state change to the checkbox
        """
        if self.checkbox.disabled:
            return

        self.checkbox.state = 'down' if self.checkbox.state == 'normal' else 'normal'
