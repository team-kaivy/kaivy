########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################


from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import kivy.clock
from kaivy.common.advanced_label import AdvancedLabel


class MessageBox(BoxLayout):
    """
    The message box class helps to easily create Android-like dialogs with YES/NO/CANCEL functionality.

    Define the on_clicked callback with parameters message box and button_index to handle the click behavior.
    """

    def __init__(self, title, text, buttons=["OK"], custom_view=None, text_width=800, close_index=-1,
                 disappear_time=None, dismissable = True):
        """
        Initializes the dialog
        :param title: The title
        :param text: The text to be displayed
        :param buttons: The buttons
        :param custom_view: An optional custom view to be attached
        :param text_width: The minimum dialog width
        :param close_index: The index of the close button if one is present
        :param disappear_time: If defined the dialogue will dismiss itself automatically in seconds
        :param dismissable: Defines if the dialog can be closed by clicking in an empty region
        """
        super().__init__()

        self.on_clicked = None  # Awaits function with parameters message box, button index
        self.on_clicked_at_index = {}  # Dictionary of callbacks, only triggered at given index, does not pass params
        self.close_index = close_index  # The index of the button which just closes the dialogue

        self.orientation = 'vertical'
        self.buttons = []  # The list of buttons
        self.text_label = AdvancedLabel(text_size=(text_width, None), text=text, size_hint=(None, None))
        self.text_label.border = (20, 28)
        self.text_label.refresh()
        self.add_widget(self.text_label)

        if custom_view is not None:
            self.add_widget(custom_view)

        if len(buttons) > 0:
            self.button_grid = BoxLayout(size_hint=(1.0, None))

            for button in buttons:
                new_button = Button(text=button, size_hint=(1.0 / len(buttons), None), height='60dp')
                self.button_grid.add_widget(new_button)
                new_button.bind(on_release=self._on_click)
                self.buttons.append(new_button)

            self.add_widget(BoxLayout(size_hint=(1.0, None), height='5dp'))

            self.add_widget(self.button_grid)

        self.do_layout()
        self.size = self.minimum_size

        # Instantiate the modal popup and display
        self.popup = Popup(title=title, size_hint=(None, None), size=(self.size[0] + 20, self.size[1] + 60),
                           content=self)
        self.popup.title_size = '18sp'
        self.popup.auto_dismiss = dismissable

        if disappear_time is not None:
            self.dismiss_timer = kivy.clock.Clock.schedule_once(self.dismiss_self, disappear_time)

    def dismiss_self(self, timer=None):
        """
        Is called when the dismiss timer is triggered
        :param timer: The timer object
        """
        self.popup.dismiss()

    def _on_click(self, bt):
        """
        Handles the button click. Triggers on_click
        :param bt: The button
        """
        try:
            index = self.buttons.index(bt)
            self.popup.dismiss()

            if self.on_clicked:
                self.on_clicked(self, index)

            if index in self.on_clicked_at_index:
                self.on_clicked_at_index[index]()

        except ValueError:
            return

    def get_popup(self):
        """
        Returns the popup, e.g. to customize dismissing behavior
        :return: The popup
        """
        return self.popup

    def get_button(self, index):
        """
        Returns the button at given index
        :param index: The button index
        :return: The button element
        """
        return self.buttons[index]

    def show(self):
        """
        Displays the dialog
        """
        self.popup.open()


class YesNoDialog(MessageBox):
    """
    A simple dialog showing a yes and a no button
    """

    def __init__(self, text, title="", yes_text="Yes", no_text="No", on_yes=None, on_no=None):
        super().__init__(title=title, text=text, buttons=[yes_text, no_text], )
        self.on_yes = on_yes  # Called if YES is clicked. Passes the dialog
        self.on_no = on_no  # Called if NO is clicked. Passes the dialog

        self.on_clicked_at_index[0] = self.handle_clicked_yes
        self.on_clicked_at_index[1] = self.handled_clicked_no

    def handle_clicked_yes(self):
        """
        Called if the yes button is clicked
        :return:
        """
        if self.on_yes is not None:
            self.on_yes(self)

    def handled_clicked_no(self):
        """
        Called if the no button is clicked
        :return:
        """
        if self.on_no is not None:
            self.on_no(self)


class OkDialog(MessageBox):
    """
    A simple dialog showing an ok button
    """

    def __init__(self, text, title="", ok_text="OK", on_ok=None, additional_buttons = [], additional_handlers={}):
        """
        Setups the dialogue
        :param text: The text to be displayed
        :param title: The title
        :param ok_text: The OK text
        :param on_ok: The OK handler
        :param additional_buttons: Texts for additional buttons
        :param additional_handlers: Event handlers for additional buttons
        """
        super().__init__(title=title, text=text, buttons=[ok_text]+additional_buttons, )
        self.on_ok = on_ok  # Called if OK is clicked. Passes the dialog

        self.on_clicked_at_index[0] = self.handle_clicked_ok
        for key, value in additional_handlers.items():
            self.on_clicked_at_index[key] = value

    def handle_clicked_ok(self):
        """
        Called if the ok button is clicked
        :return:
        """
        if self.on_ok is not None:
            self.on_ok(self)


if __name__ == '__main__':  # Most minimal test application
    from kivy.base import runTouchApp
    from kivy.uix.gridlayout import GridLayout
    from kivy.core.window import Window

    dialog = YesNoDialog("Is the banana bend?", "Important question", on_yes=lambda m: OkDialog("Yes it is!").show(),
                         on_no=lambda m: OkDialog("Really? :(").show())
    layout = GridLayout(cols=3)
    Window.add_widget(layout)
    Window.size = (1280, 800)
    button = Button(text="Click me", on_release=lambda x: dialog.show())
    layout.add_widget(button)
    dialog.show()

    runTouchApp()
