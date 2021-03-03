########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################
"""
  This file defines the ImageButton control which allows the usage of predesigned PNGs to be used as UI elements
"""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.label import Label

from kaivy.common.advanced_image import AdvancedImage


class ImageButton(ButtonBehavior, AdvancedImage):
    """
    The image button allows the usage of images as button controls
    """

    def __init__(self):
        """
        Initializer
        """
        super(ImageButton, self).__init__()
        self.size_hint = (None, None)
        self.up_state_image = None
        self.down_state_image = None

    def set_images(self, up_state, down_state=None, file_list=None, base_path=None):
        """
        Sets the images for up and down state
        :param up_state: Name of the image file for the up state
        :param down_state: Name of the image file for the down state
        :param file_list: A list of image file names
        :param base_path: The base path to be added
        """
        if file_list is not None:
            up_state = file_list[0] if len(file_list) > 0 else None
            down_state = file_list[1] if len(file_list) > 1 else None
        base_path = base_path if base_path is not None else ""
        if up_state is not None and isinstance(up_state, str):
            self.up_state_image = base_path + up_state
        else:
            self.up_state_image = up_state
        if down_state is not None and isinstance(down_state, str):
            self.down_state_image = base_path + down_state
        else:
            self.down_state_image = down_state
        if self.down_state_image is None:
            self.down_state_image = self.up_state_image
        self.set_current_image(self.up_state_image)

    def set_current_image(self, new_image):
        if isinstance(new_image, str):
            self.source = new_image
            if self.auto_size:
                self.handle_auto_size()
        elif new_image is not None:
            self.set_image_data(new_image)

    def on_touch_up(self, touch):
        """
        Called on release anywhere
        """
        if not self.collide_point(*touch.pos):
            return

        super().on_touch_up(touch)
        self.set_current_image(self.up_state_image)

    def on_press(self):
        """
        Called on press
        """
        self.set_current_image(self.down_state_image)

    def on_release(self):
        """
        Called on release
        """
        self.set_current_image(self.up_state_image)


class AdvancedImageButton(FloatLayout):
    """
    Defines an advanced buttons which supports being labeled and a down state
    """

    TEXT_LOCATION_BOTTOM = "bottom"
    TEXT_LOCATION_TOP = "top"

    def __init__(self):
        """
        Initializer
        :param kwargs:
        """
        super().__init__()

        self.is_down = False  # Defines if the button is currently down
        self.is_pressed = False  # Defines if the button is pressed down
        self.was_pressed = True  # Defines if the button was previously pressed
        self.stays_down = False  # Defines if the button stays down
        self.on_down = None  # Is triggered when the button entered the down state
        self.size_hint = (None, None)
        self.image_scaling = 1.0
        self.image_view = ImageButton()
        self.image_view.allow_stretch = True
        self.image_view.auto_size = False
        self.add_widget(self.image_view)
        self.text_location = self.TEXT_LOCATION_BOTTOM  # Defines where the text shall be placed
        self.label_padding = 4.0  # Padding in case text is not centered
        self.label = None
        self.border_rect = InstructionGroup()
        self.canvas.add(self.border_rect)
        self.image_view.bind(on_press=self.button_pressed)
        self.image_view.bind(on_release=self.button_released)
        self.image_view.bind(on_touch_up=self.touch_released)
        self.button_border_size = 2  # The size of the button border
        self.click_border_color = Color(1, 1, 1, 1)
        self.default_border_color = Color(0, 0, 0, 1)

    def set_label(self, text, text_location=None, font_size='14 sp', color=(0, 0, 0, 1), outline_color=(0, 0, 0, 1),
                  outline_width=1):
        """
        Adds a label to the button which can be shown at it's bottom or center
        :param text: The label's text
        :param text_location: The text's location. Bottom by default
        :param font_size: The font's size as string, e.g 14sp or 14px
        :param color: The text color as RGBA tuple
        :param outline_color: The outline color as RGBA tuple
        :param outline_width: The outline's size
        :return:
        """

        if self.label:
            self.remove_widget(self.label)
            self.label = None
        self.label = Label(text=text, font_size=font_size, size_hint=(None, None))
        self.label.halign = 'center'
        self.text_location = text_location
        if self.text_location is None:
            self.text_location = self.TEXT_LOCATION_BOTTOM
        self.label.bold = True
        self.label.color = Color(color[0], color[1], color[2], color[3])
        self.label.outline_color = Color(outline_color[0], outline_color[1], outline_color[2], outline_color[3])
        self.label.outline_width = outline_width
        self.label.bind(texture_size=self.label_tex_change)
        self.add_widget(self.label)

    def label_tex_change(self, lt, size):
        """
        Automatically resize label when it's texture changed
        :param lt:
        :param size:
        """
        lt.size = (size[0], size[1])
        self.update_sizes()

    def do_layout(self, *largs):
        super().do_layout(*largs)
        if self.label is not None:
            if self.text_location == self.TEXT_LOCATION_BOTTOM == False:
                self.image_view.pos = (self.pos[0], self.pos[1] + self.label.height + self.label_padding)
                self.label.pos = self.pos
            else:
                self.label.pos = (self.pos[0], self.pos[1] + self.height // 2 - self.label.height // 2)
                self.image_view.pos = self.pos
        else:
            self.image_view.pos = self.pos

        self.update_pressed_state()

    def update_pressed_state(self):
        """
        Updates the drawing behavior when the button has been pressed or released
        """
        self.set_image_scaling(1.2 if self.is_down or self.is_pressed else 1.0)
        border_size = self.button_border_size
        self.border_rect.clear()
        if border_size > 0:
            if self.is_pressed or self.is_down:
                self.border_rect.add(self.click_border_color)
            else:
                self.border_rect.add(self.default_border_color)
            self.border_rect.add(Rectangle(pos=self.image_view.pos, size=(self.image_view.width, border_size)))
            self.border_rect.add(
                Rectangle(pos=(self.image_view.pos[0], self.image_view.pos[1] + self.image_view.height - border_size),
                          size=(self.image_view.width, border_size)))
            self.border_rect.add(Rectangle(pos=(self.image_view.pos[0], self.image_view.pos[1] + border_size),
                                           size=(border_size, self.image_view.height - 2 * border_size)))
            self.border_rect.add(Rectangle(pos=(
                self.image_view.pos[0] + self.image_view.width - 1 * border_size, self.image_view.pos[1] + border_size),
                size=(border_size, self.image_view.height - 2 * border_size)))

    def update_sizes(self):
        """
        Updates all sizes when a new texture was applied or the text has been modified
        :return:
        """
        eff_size = (
            self.image_view.texture_size[0] * self.image_scaling, self.image_view.texture_size[1] * self.image_scaling)
        self.image_view.size = eff_size
        if self.label is not None:
            if self.center_text == False:
                eff_size = (eff_size[0], eff_size[1] + self.label.height + self.label_padding * 2)
                self.image_view.pos = (self.pos[0], self.pos[1] + self.label.height + self.label_padding)
        self.size = eff_size

    def set_images(self, up_state, down_state=None, file_list=None, base_path=None):
        """
        Sets the images for up and down state
        :param up_state: Name of the image file for the up state
        :param down_state: Name of the image file for the down state
        :param file_list: A list of image file names
        :param base_path: The base path to be added
        """
        self.image_view.set_images(up_state, down_state, file_list=file_list, base_path=base_path)
        self.image_view.handle_auto_size()
        if self.label is not None:
            self.label.text_size = (self.image_view.texture_size[0], None)
        self.update_sizes()
        self.do_layout()

    def set_image_scaling(self, value):
        """
        Updates the images size, e.g. when it's selected
        :param value:
        :return:
        """
        self.image_scaling = value
        self.update_sizes()

    def button_pressed(self, bt):
        """
        Is called when the button is pressed
        :param bt:
        :return:
        """
        self.canvas.ask_update()
        self.is_pressed = True
        self.was_pressed = False
        self.update_pressed_state()

    def button_released(self, bt):
        """
        Is called when the button is released
        :param bt:
        :return:
        """
        self.canvas.ask_update()
        self.set_image_scaling(1.0)
        if self.is_pressed or self.was_pressed:
            if self.stays_down:
                self.set_down(True)
        self.is_pressed = False
        self.update_pressed_state()

    def touch_released(self, bt, loc):
        """
        Is called when the button is released, including outside
        :param bt:
        :param loc:
        :return:
        """
        self.is_pressed = False
        self.was_pressed = True
        self.update_pressed_state()

    def set_down(self, state):
        """
        Updates the button's down state
        :param state: The new state
        """
        if self.is_down == state:
            return
        self.is_down = state
        if state and self.on_down is not None:
            self.on_down(self)
        self.update_pressed_state()


class ImageButtonBar(BoxLayout):
    """
    A list of image buttons of which one can be selected
    """

    SIDE_BOTTOM = 'bottom'  # Dock the bar to the bottom

    def __init__(self, **kwargs):
        """
        Initializer
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.index = -1
        self.buttons = []
        self.identifiers = []
        self.button_spacing = '15dp'  # Defines the space between each button
        self.docking_side = self.SIDE_BOTTOM  # The docking site
        self.on_index_changed = None  # Function which is called when the index does change. Receives view and new index

    def add_button(self, image_up, image_down=None, identifier=""):
        """
        Adds a button
        :param image_up: The image for the up state
        :param image_down: The image for the down state
        :param identifier: The identifier
        :return: Returns the button for further customization
        """
        if len(self.buttons):
            self.add_widget(BoxLayout(size_hint=(None, 1.0), width=self.button_spacing))
        button = AdvancedImageButton()
        button.set_images(image_up, image_down)
        button.stays_down = True
        button.on_down = self.handle_down_state_changed
        self.add_widget(button)
        self.buttons.append(button)
        self.identifiers.append(identifier)
        return button

    def set_images(self, index, image_up, image_down=None):
        """
        Sets the images for the button at given index
        :param index: The button index
        :param image_up: The image for the up state
        :param image_down: The image for the down state
        """
        if 0 <= index < len(self.buttons):
            self.buttons[index].set_images(image_up, image_down)

    def set_index(self, index):
        """
        Set the index of the selected button and update all down states
        :param index: The new index
        """
        if self.index == index:
            return
        self.index = index
        for cur_index, button in enumerate(self.buttons):
            if cur_index != index:
                button.set_down(False)
            else:
                button.set_down(True)
        if self.on_index_changed is not None:
            self.on_index_changed(self, index)

    def handle_down_state_changed(self, view):
        index = -1
        try:
            index = self.buttons.index(view)
        except ValueError:
            pass
        if index != -1:
            self.set_index(index)
